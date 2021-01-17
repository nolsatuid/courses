import typing

from django.shortcuts import redirect, get_object_or_404
from fortuna_client.callback import RemoteTransactionCallback
from fortuna_client.transaction import RemoteTransaction

from nolsatu_courses.apps.courses.models import Courses, Enrollment
from nolsatu_courses.apps.products.models import Order, OrderItem


class FortunaCallback(RemoteTransactionCallback):
    def on_callback(self, transaction: RemoteTransaction):
        remote_status_map = {
            RemoteTransaction.Status.CREATED: Order.STATUS.created,
            RemoteTransaction.Status.SUCCESS: Order.STATUS.success,
            RemoteTransaction.Status.PENDING: Order.STATUS.pending,
            RemoteTransaction.Status.FAILED: Order.STATUS.failed,
            RemoteTransaction.Status.EXPIRED: Order.STATUS.expired,
            RemoteTransaction.Status.REFUND: Order.STATUS.refund,
            RemoteTransaction.Status.OTHER: Order.STATUS.other,
        }

        current_order: typing.Optional[Order] = Order.objects.filter(remote_transaction_id=transaction.id).first()

        if not current_order:
            return

        if current_order.status not in (Order.STATUS.pending, Order.STATUS.created):
            return

        current_order.status = remote_status_map[transaction.status]
        current_order.save()

        if current_order.status == Order.STATUS.success:
            # Enroll User
            order_item: OrderItem
            for order_item in current_order.orders.all():
                course: Courses = order_item.product.course
                if not course.has_enrolled(current_order.user):
                    course.enrolled.create(
                        course=course, user=current_order.user,
                        batch=course.batchs.last(), allowed_access=True,
                        status=Enrollment.STATUS.begin
                    )

        # Notify User
        notification_status = [Order.STATUS.success, Order.STATUS.failed, Order.STATUS.expired, Order.STATUS.refund]
        if current_order.status in notification_status:
            current_order.notify_user(transaction)

    def payment_redirect(self, request, transaction_id, order_id):
        order = get_object_or_404(Order, user=request.user, remote_transaction_id=transaction_id)
        return redirect("website:orders:details", order_id=order.id)
