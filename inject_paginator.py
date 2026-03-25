import os
import re

templates = {
    'admin_users.html': '?page={{ p }}&search={{ search }}&date_joined={{ date_joined }}',
    'admin_inventory.html': '?page={{ p }}&search={{ search }}&date_created={{ date_created }}&price_type={{ price_type }}&price_range={{ price_range }}',
    'admin_sales.html': '?page={{ p }}&search={{ search }}&date={{ date }}'
}

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

for filename, query_str in templates.items():
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 1: Strip existing Pagination blocks if they exist
    content = re.sub(r'<!-- Pagination -->.*?</div>\s*</div>\s*</div>\s*(?:{% endif %})?', '</div>\n</div>\n', content, flags=re.DOTALL)
    
    # We will inject right before `</div><!-- /#salesContainer -->` in sales, and similarly for others.
    # What's the best anchor? `</table>` and its immediate wrapper `</div>` closures.
    
    pagination_html = f"""
                <!-- Pagination -->
                <div class="pagination-container" style="padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size:13px; color:var(--text-muted); font-weight:500;">Page {{{{ page }}}} of {{{{ total_pages }}}}</span>
                    <div style="display:flex; gap:6px;">
                        {{% if page > 1 %}}
                        {{% set p = page - 1 %}}
                        <a href="{query_str}" class="btn-sm" style="background:var(--card-bg); border:1px solid var(--border); color:var(--text-muted);"><i class="fas fa-chevron-left"></i> Prev</a>
                        {{% else %}}
                        <span class="btn-sm" style="background:var(--card-bg); border:1px solid var(--border); color:#cbd5e1; cursor:not-allowed;"><i class="fas fa-chevron-left"></i> Prev</span>
                        {{% endif %}}
                        
                        {{% for p in range(1, total_pages + 1) %}}
                            {{% if p == 1 or p == total_pages or (p >= page - 2 and p <= page + 2) %}}
                                <a href="{query_str}" class="btn-sm" style="{{% if p == page %}}background:var(--green); color:#fff; border:1px solid var(--green); cursor:default;{{% else %}}background:var(--card-bg); border:1px solid var(--border); color:var(--text-muted);{{% endif %}}">{{{{ p }}}}</a>
                            {{% elif p == page - 3 or p == page + 3 %}}
                                <span class="btn-sm" style="background:transparent; color:var(--text-muted); cursor:default;">...</span>
                            {{% endif %}}
                        {{% endfor %}}
                        
                        {{% if page < total_pages %}}
                        {{% set p = page + 1 %}}
                        <a href="{query_str}" class="btn-sm" style="background:var(--card-bg); border:1px solid var(--border); color:var(--text-muted);">Next <i class="fas fa-chevron-right"></i></a>
                        {{% else %}}
                        <span class="btn-sm" style="background:var(--card-bg); border:1px solid var(--border); color:#cbd5e1; cursor:not-allowed;">Next <i class="fas fa-chevron-right"></i></span>
                        {{% endif %}}
                    </div>
                </div>
"""
    
    # Let's dynamically find the `</table>` tag and the next `</div>` tag and inject between or after them safely.
    if filename == 'admin_sales.html':
        # In sales, it's </table> \n </div> \n </div>
        content = re.sub(r'(</table>\s*</div>\s*</div>)', r'\1' + '\n' + pagination_html, content)
    else:
        # In users and inventory, it's </table> \n </div>
        content = re.sub(r'(</table>\s*</div>)', r'\1' + '\n' + pagination_html, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Updated pagination in {filename}")
