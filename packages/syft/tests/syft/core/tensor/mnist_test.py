# third party
import numpy as np
import torch as th

# syft absolute
import syft as sy
from syft import deserialize
from syft import serialize
from syft.core.adp.entity import Entity
from syft.core.tensor.tensor import Tensor


def test_vs_torch() -> None:
    data_batch = np.random.rand(4, 28 * 28)
    label_batch = np.random.rand(4, 10)
    data = Tensor(data_batch).autograd(requires_grad=True)
    target = Tensor(label_batch).autograd(requires_grad=True)

    weights = np.random.rand(28 * 28, 10)

    pred = data.dot(weights)
    diff = target - pred
    pre_loss = np.square(diff)

    pre_loss.backward()
    pred.grad

    th_data = th.tensor(data.child.child, requires_grad=True)
    th_target = th.tensor(target.child.child, requires_grad=True)
    th_weights = th.tensor(weights, requires_grad=True)

    th_pred = th.tensor(th_data.mm(th_weights), requires_grad=True)
    th_diff = th_target - th_pred
    th_pre_loss = th_diff * th_diff

    th_pre_loss.sum().backward()
    th_pred.grad

    assert diff == th_diff.clone().detach().numpy()
    assert pre_loss == th_pre_loss.clone().detach().numpy()
    assert pred == th_pred.clone().detach().numpy()
    assert pred.grad == th_pred.grad.clone().detach().numpy()


def test_train_mnist() -> None:
    data_batch = np.random.rand(4, 28 * 28)
    label_batch = np.random.rand(4, 10)

    bob = Entity(unique_name="Bob")

    data = Tensor(data_batch).private(0.01, 1, entity=bob).autograd(requires_grad=True)
    target = (
        Tensor(label_batch).private(0.01, 1, entity=bob).autograd(requires_grad=True)
    )

    weights = Tensor(np.random.rand(28 * 28, 10)).autograd(requires_grad=True)

    for i in range(10):
        pred = data.dot(weights)
        diff = target - pred
        pre_loss = np.square(diff)
        loss = np.mean(pre_loss)
        _ = -diff
        loss.backward()

        wdiff = weights.grad * 0.01
        weights = -wdiff + weights

    assert loss.data_child < 10.0


def test_serde_tensors() -> None:
    data = np.random.rand(4, 10)
    bob = Entity(unique_name="Bob")

    # Step 1: upload a private dataset as the root owner
    data = (
        Tensor(data)
        .private(0.01, 1, entity=bob)
        .autograd(requires_grad=True)
        .tag("data")
    )

    ser = serialize(data)

    de = deserialize(ser)

    comp_left = data
    comp_right = de

    assert type(comp_left) == type(comp_right)
    while hasattr(comp_left, "child"):
        comp_left = comp_left.child
        comp_right = comp_right.child
    assert not hasattr(comp_left, "child")
    assert not hasattr(comp_right, "child")
    assert type(comp_left) == type(comp_right)

    assert (de.data_child == data.data_child).all()


def test_send_tensors(root_client: sy.VirtualMachineClient) -> None:
    data = np.random.rand(4, 10)
    bob = Entity(unique_name="Bob")

    # Step 1: upload a private dataset as the root owner
    data = Tensor(data).private(0.01, 1, entity=bob).autograd(requires_grad=True)
    data_ptr = data.send(root_client, tags=["data"])
    assert len(root_client.store) == 1

    res = data_ptr.get()

    comp_left = data
    comp_right = res

    assert type(comp_left) == type(comp_right)
    while hasattr(comp_left, "child"):
        comp_left = comp_left.child
        comp_right = comp_right.child
    assert not hasattr(comp_left, "child")
    assert not hasattr(comp_right, "child")
    assert type(comp_left) == type(comp_right)

    assert (res.data_child == data.data_child).all()


def test_basic_publish_event() -> None:
    domain = sy.Domain("My Amazing Domain", max_budget=10)
    root_client = domain.get_root_client()

    data_batch = np.random.rand(4, 28 * 28)
    label_batch = np.random.rand(4, 10)

    bob = Entity(unique_name="Bob")

    # Step 1: upload a private dataset as the root owner
    data = (
        Tensor(data_batch)
        .private(0.01, 1, entity=bob)
        .autograd(requires_grad=True)
        .tag("data")
    )

    target = (
        Tensor(label_batch).private(0.01, 1, entity=bob).autograd(requires_grad=True)
    ).tag("target")

    data.send(root_client)
    target.send(root_client)

    # Step 2: user connects to domain with a new verify_key
    client = domain.get_client()

    data_ptr = client.store["data"]
    target_ptr = client.store["target"]

    weights = Tensor(np.random.rand(28 * 28, 10)).autograd(requires_grad=True)
    weights_ptr = weights.send(client)

    for i in range(1):
        pred = data_ptr.dot(weights_ptr)
        diff = target_ptr - pred

        pre_loss = np.square(diff)  # cant use
        # pre_loss = diff * diff

        loss = np.mean(pre_loss)  # cant use
        # loss = pre_loss.sum() / pre_loss.len()
        loss.backward()

        wdiff = weights_ptr.grad * 0.01
        weights_ptr = -wdiff + weights_ptr

    # acc should default to client.accountant
    # TODO: @Madhava implement
    # weights_ptr_downloadable = weights_ptr.publish(acc=client.accountant, sigma=0.1)
    # weights = weights_ptr_downloadable.get()
    updated_weights = weights_ptr.get()
    assert not (updated_weights.data_child == weights.data_child).all()


# TODO: @Madhava Make work
# def test_simulated_publish_event() -> None:
#     domain = sy.Domain("My Amazing Domain", max_budget=10)
#     root_client = domain.get_root_client()
#
#     data_batch = np.random.rand(4, 28 * 28)
#     label_batch = np.random.rand(4, 10)
#
#     bob = Entity(unique_name="Bob")
#
#     # Step 1: upload a private dataset as the root owner
#     data = Tensor(data_batch).private(0.01, 1, entity=bob).autograd(requires_grad=True).tag("data")
#     target = (
#         Tensor(label_batch).private(0.01, 1, entity=bob).autograd(requires_grad=True)
#     ).tag("target")
#
#     root_client.send(data)
#     root_client.send(target)
#
#     # Step 2: user connects to domain
#
#     # (this has a new verify key)
#     client = domain.get_client()
#
#     data = client.store['data']
#     target = client.store['target']
#
#     weights = Tensor(np.random.rand(28 * 28, 10)).autograd(requires_grad=True)
#     weights_ptr = weights.send(client)
#
#     for i in range(10):
#         pred = data.dot(weights_ptr)
#         diff = target - pred
#         pre_loss = np.square(diff)
#         loss = np.mean(pre_loss)
#         extraneous_thing = -diff
#         loss.backward()
#
#         wdiff = weights_ptr.grad * 0.01
#         weights_ptr = -wdiff + weights_ptr
#
#     # init_with_budget_remaining shoudl default to true
#     simulated_accountant = client.create_simulated_accountant(init_with_budget_remaining=True)
#
#     weights_ptr_downloadable = weights_ptr.publish(acc=simulated_accountant, sigma=0.1)
#
#     # return pointer to GammaScalar
#     ptr_to_budget = simulated_accountant.calculate_remaining_budget()
#
#     # publish GammaScalar like you would normally
#     downloadable_budget = ptr_to_budget.publish(acc=client.accountant, sigma=0.1)
#     print(downloadable_budget.get())