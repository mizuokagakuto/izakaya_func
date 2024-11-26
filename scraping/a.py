"""
span_element = soup.find('span', class_='rstinfo-table__budget-item')

if span_element:  # span タグが存在するか確認
    i_element = span_element.find('i', class_='c-rating-v3__time c-rating-v3__time--dinner')
    
    if i_element:  # 該当クラスの i タグが存在するか確認
        price_range = span_element.find('em').text
        print("  口コミ予算:{}".format(price_range), end="")
    else:
        print("  予算:ディナーの予算がありません", end="")
else:
    print("  口コミ予算:予算情報が見つかりません", end="")
"""