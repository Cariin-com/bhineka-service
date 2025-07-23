def parse_product_page(soup):
    # Name
    name_tag = soup.find("h1", attrs={"itemprop": "name"})
    name = name_tag.text.strip() if name_tag else "Unknown"

    # Price (ambil dari span[itemprop=price] yang hidden, fallback ke harga yang terlihat)
    price_tag = soup.find("span", attrs={"itemprop": "price"})
    if price_tag and price_tag.get("style", "").find("display:none") != -1:
        price = price_tag.text.strip()
    else:
        # fallback: cari harga yang terlihat
        price_visible = soup.find("span", class_="oe_currency_value")
        price = price_visible.text.strip() if price_visible else "Unknown"

    # SKU (dari input[name=sku] atau div.sku-rating)
    sku_input = soup.find("input", attrs={"name": "sku"})
    if sku_input and sku_input.has_attr("value"):
        sku = sku_input["value"].strip()
    else:
        sku_div = soup.find("div", class_="sku-rating")
        sku = sku_div.text.strip() if sku_div else "Unknown"

    # Images (dari span[itemprop=image] yang hidden)
    images = []
    image_tag = soup.find("span", attrs={"itemprop": "image"})
    if image_tag and image_tag.get("style", "").find("display:none") != -1:
        images.append(image_tag.text.strip())

    # Estimate pengiriman (dari span#productHandlingTimeInformation)
    estimate = ""
    est_span = soup.find("span", id="productHandlingTimeInformation")
    if est_span:
        estimate = est_span.get_text(strip=True)

    # Store info (dari div.row dengan strong 'Informasi Toko')
    store_info = ""
    for row in soup.find_all("div", class_="row"):
        strong = row.find("strong")
        if strong and "Informasi Toko" in strong.get_text():
            col = row.find("div", class_="col-sm-9")
            if col:
                store_info = col.get_text(strip=True)
            break

    # Warranty (dari div.row dengan strong 'Garansi')
    warranty = ""
    for row in soup.find_all("div", class_="row"):
        strong = row.find("strong")
        if strong and "Garansi" in strong.get_text():
            col = row.find("div", class_="col-sm-9")
            if col:
                warranty = col.get_text(strip=True)
            break

    # Spesifikasi produk dari table (misal class 'table' atau 'specs-table')
    specs = {}
    for table in soup.find_all("table"):
        table_class = table.get("class", [])
        if "table" in table_class or "specs-table" in table_class or not table_class:
            for row in table.find_all("tr"):
                cols = row.find_all(["td", "th"])
                if len(cols) >= 2:
                    key = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    if key and value:
                        if key in specs:
                            specs[key] += ", " + value
                        else:
                            specs[key] = value

    # Spesifikasi produk dari <ul> list (key: strong, value: span atau text setelah strong)
    for ul in soup.find_all("ul"):
        for li in ul.find_all("li", recursive=False):
            strong = li.find("strong")
            if strong:
                key = strong.get_text(strip=True)
                value = strong.next_sibling
                if value:
                    value = value.strip()
                else:
                    span = strong.find_next("span")
                    value = span.get_text(strip=True) if span else None
                if key and value:
                    if key in specs:
                        specs[key] += ", " + value
                    else:
                        specs[key] = value

    # Spesifikasi produk dari <dl> (key: dt, value: dd)
    for dl in soup.find_all("dl"):
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            key = dt.get_text(strip=True)
            value = dd.get_text(strip=True)
            if key and value:
                if key in specs:
                    specs[key] += ", " + value
                else:
                    specs[key] = value

    # Spesifikasi produk (key dari strong.attribute_name, value dari span di label radio_input_value o_variant_pills_input_value yang checked/active)
    specs_list = soup.find("ul", class_="js_add_cart_variants")
    if specs_list:
        for li in specs_list.find_all("li", recursive=False):
            key_tag = li.find("strong", class_="attribute_name")
            key = key_tag.text.strip() if key_tag else None
            value = None
            ul_values = li.find("ul", class_="o_wsale_product_attribute")
            if ul_values:
                for value_li in ul_values.find_all("li", class_="js_attribute_value"):
                    input_tag = value_li.find("input", attrs={"type": "radio"})
                    if input_tag and input_tag.has_attr("checked"):
                        label = value_li.find("label", class_="radio_input_value")
                        if label:
                            span_value = label.find("span")
                            if span_value:
                                value = span_value.text.strip()
                                break
            if key and value:
                if key in specs:
                    specs[key] += ", " + value
                else:
                    specs[key] = value

    # Ketersediaan (dari id=product_unavailable, jika ada berarti tidak tersedia, jika tidak ada berarti "Available")
    unavailable = soup.find(id="product_unavailable")
    availability = "Unavailable" if unavailable and unavailable.get("class") and "d-none" not in unavailable["class"] else "Available"

    return {
        "name": name,
        "price": price,
        "sku": sku,
        "images": images,
        "specs": specs,
        "availability": availability,
        "estimate": estimate,
        "store_info": store_info,
        "warranty": warranty
    }
