import requests
import time
import re
from bs4 import BeautifulSoup


def extract_cable_info(url):
    time.sleep(2)  # Delay to avoid getting blocked by the website

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
        })
        response = session.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        cable_rows = soup.find_all('tr')
        results = []

        for row in cable_rows:
            product_td = row.find('td')  # Get product information
            price_td = row.find('td', class_='wy-price-sep')  # Get price information

            if product_td and price_td:
                product_text = product_td.get_text(strip=True)  # Extract full product name
                size_match = product_td.find('strong')  # Extract cable size

                # Validate product type: must contain "کابل افشان" or "سیم افشان"
                if "کابل افشان" in product_text:
                    product_type = "Cable"
                elif "سیم افشان" in product_text:
                    product_type = "Wire"
                else:
                    continue  # Skip unrelated products

                # Extract size information if found
                size = size_match.get_text(strip=True) if size_match else None
                if size and '+' in size:
                    continue  # Skip sizes with "+" (combined sizes)

                # Extract price and convert it to an integer
                price_text = price_td.get_text(strip=True)
                try:
                    price = int(price_text.replace(',', '').strip())
                except ValueError:
                    price = None  # Handle cases where price conversion fails

                # Extract brand name (assuming the brand is "Khorasan Afsharnejad")
                brand_match = re.search(r'خراسان افشارنژاد', product_text)
                brand = "Khorasan" if brand_match else None

                # Format size for structured output
                if size:
                    size = size.replace('/', '.')  # Standardize size format
                    if '×' in size:
                        l_number = int(size.split('×')[0])
                        l_size = float(size.split('×')[1])
                    else:
                        l_number = 1
                        l_size = float(size)
                else:
                    l_number, l_size = None, None  # Handle missing size

                results.append({
                    'l_number': l_number,
                    'l_size': l_size,
                    'brand': brand,
                    'type': product_type,
                    'note': "Flexible",
                    'price': price
                })

        # Return results or an error message if no relevant products are found
        if not results:
            return False, "No matching cables or wires found"
        return True, results

    except Exception as e:
        return False, f"Error while fetching: {e}"


# Example usage
url = "https://www.barghsan.com/لیست-قیمت-سیم-و-کابل-خراسان-افشارنژاد/"
success, data = extract_cable_info(url)
if success:
    for cable in data:
        print(cable)
else:
    print("Error:", data)
