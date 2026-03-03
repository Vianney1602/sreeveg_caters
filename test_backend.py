import requests

r = requests.post("http://127.0.0.1:8000/api/payments/verify", json={
    "payment_id": "pay_test",
    "order_id": "order_test",
    "razorpay_order_id": "order_test",
    "razorpay_signature": "sig"
})
print("Result:", r.status_code, r.text)
