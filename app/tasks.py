from django.utils.timezone import now
from django.db.models import Sum, F, DecimalField
from .models import Order, Report

def generate_daily_sales_report():
    today = now().date()
    Report.objects.filter(report_type="sales", generated_at__date=today).delete()

    sales_data = (Order.objects.filter(ordered_at__date=today, status="completed")
        .values("product__name")
        .annotate(
            total_sold=Sum("quantity"),
            total_price=Sum(F("quantity") * F("product__price"), output_field=DecimalField())
        ))

    total_revenue = sum(item["total_price"] for item in sales_data)
    report_lines = ["📊 **Sales Report - {}**\n".format(today.strftime("%B %d, %Y"))]
    
    for item in sales_data:
        report_lines.append(f"🔹 {item['product__name']}: {item['total_sold']} units |  ${item['total_price']:.2f}")

    report_lines.append(f"\n📌 **Total Revenue:**  ${total_revenue:.2f}")
    Report.objects.create(report_type="sales", details="\n".join(report_lines))
    print("✅ Daily sales report generated successfully!")
