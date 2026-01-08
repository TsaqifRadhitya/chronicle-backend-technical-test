from celery import shared_task

@shared_task
def process_order(order_id):
    print(f"Order #{order_id} Processed.")
