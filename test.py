import pandas as pd

# مسیر خروجی فایل
output_path = r"C:\Users\a.tavakoliniya\Desktop\generated_report.xlsx"

# داده نمونه برای درج در جدول
data = [
    [1, "تابلو بگ فیلتر", 1, 3700564000, 3700564000, 0, 0, 0],
    [2, "ابزار دقیق", 1, 1690000000, 1690000000, 0, 0, 0],
]

# ایجاد DataFrame با ستون‌های اصلی
df = pd.DataFrame(data, columns=["خرید", "مهندسی", "ساخت", "قیمت کل(ریال)", "قیمت", "تعداد", "شرح", "ردیف"])

# شروع نوشتن فایل با xlsxwriter
with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    workbook = writer.book
    worksheet = workbook.add_worksheet("قیمت نهایی")
    writer.sheets["قیمت نهایی"] = worksheet

    # قالب‌های مورد استفاده
    header_format = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter',
        'border': 1, 'text_wrap': True
    })
    cell_format = workbook.add_format({
        'border': 1, 'align': 'center', 'valign': 'vcenter'
    })

    # نوشتن هدرهای ترکیبی (3 ردیف اول)
    worksheet.merge_range('B1:J1', 'قیمت و نفر ساعت تقریبی یک پروژه مشابه', header_format)
    worksheet.write('B2', 'ردیف', header_format)
    worksheet.write('C2', 'شرح', header_format)
    worksheet.write('D2', 'تعداد', header_format)
    worksheet.write('E2', 'قیمت', header_format)
    worksheet.write('F2', 'قیمت کل(ریال)', header_format)
    worksheet.merge_range('G2:J2', 'نفر ساعت واحد', header_format)

    # سطر سوم - زیرعنوان‌ها
    worksheet.write('G3', '', header_format)
    worksheet.write('H3', 'ساخت', header_format)
    worksheet.write('I3', 'مهندسی', header_format)
    worksheet.write('J3', 'خرید', header_format)

    # نوشتن داده‌ها
    for row_idx, row in df.iterrows():
        worksheet.write(row_idx + 3, 1, row["ردیف"], cell_format)
        worksheet.write(row_idx + 3, 2, row["شرح"], cell_format)
        worksheet.write(row_idx + 3, 3, row["تعداد"], cell_format)
        worksheet.write(row_idx + 3, 4, row["قیمت"], cell_format)
        worksheet.write(row_idx + 3, 5, row["قیمت کل(ریال)"], cell_format)
        worksheet.write(row_idx + 3, 7, row["ساخت"], cell_format)
        worksheet.write(row_idx + 3, 8, row["مهندسی"], cell_format)
        worksheet.write(row_idx + 3, 9, row["خرید"], cell_format)

    # تنظیم عرض ستون‌ها
    worksheet.set_column('B:B', 6)   # ردیف
    worksheet.set_column('C:C', 25)  # شرح
    worksheet.set_column('D:F', 15)  # تعداد، قیمت، قیمت کل
    worksheet.set_column('H:J', 12)  # نفر ساعت‌ها
