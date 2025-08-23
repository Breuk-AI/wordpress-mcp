# WordPress MCP Examples - Real Conversations, Real Results

> *Actual conversations between humans and Claude using WordPress MCP*

## 📝 Content Management Examples

### Creating a Blog Post
```
Human: Create a blog post about the benefits of meditation, make it SEO friendly

Claude: I'll create an SEO-optimized blog post about meditation benefits for you.

*[Creates post with title, meta description, proper headings, and keywords]*

✅ Created post "10 Science-Backed Benefits of Daily Meditation" 
   - Status: Draft
   - ID: 1247
   - SEO Score: Excellent
   - Word Count: 1,200
   
Would you like me to publish it or would you prefer to review it first?
```

### Bulk Content Updates
```
Human: Add a disclaimer to all posts in the "Health" category

Claude: I'll add a disclaimer to all posts in the Health category.

*[Searching posts...]*
Found 23 posts in "Health" category.

*[Updating posts...]*
✅ Updated 23 posts with disclaimer
   - Added to post footer
   - Preserves existing content
   - Backup created: health-posts-backup-2024-01-19.json
```

### Finding and Fixing Content
```
Human: Find all posts mentioning "2023" and update them to "2024"

Claude: I'll search for all posts containing "2023" and update them to "2024".

*[Searching content...]*
Found 47 posts containing "2023"

*[Creating backup...]*
Backup saved: posts-2023-to-2024-backup.json

*[Updating posts...]*
✅ Updated 47 posts
   - 112 instances of "2023" replaced with "2024"
   - Titles: 8 updated
   - Content: 104 updated
   - All changes logged
```

## 🛒 WooCommerce Magic

### Price Management
```
Human: Increase all prices by 15% but round to nearest .99

Claude: I'll increase all product prices by 15% and round to .99 pricing.

*[Fetching products...]*
Found 156 products

*[Calculating new prices...]*
Examples:
- "Classic Tee" $19.99 → $22.99
- "Premium Hoodie" $49.99 → $56.99
- "Canvas Bag" $14.99 → $16.99

*[Updating prices...]*
✅ Updated 156 product prices
   - Average increase: $4.27
   - Highest: $89.99 → $102.99
   - All prices end in .99
```

### Inventory Management
```
Human: Show me products with less than 5 items in stock

Claude: I'll find all products with low stock (less than 5 items).

*[Checking inventory...]*

⚠️ Low Stock Alert - 12 products:

1. "Vintage Tee" - 2 left (Best seller!)
2. "Classic Hoodie" - 0 left (Out of stock!)
3. "Eco Water Bottle" - 4 left
4. "Canvas Tote" - 1 left
5. "Bamboo Notebook" - 3 left
...and 7 more

Would you like me to:
- Set these to "backorder allowed"?
- Create a purchase order?
- Send low stock notifications?
```

### Order Processing
```
Human: Show me today's orders and their status

Claude: I'll fetch today's orders for you.

*[Retrieving orders...]*

📦 Today's Orders (January 19, 2024):

Total: 23 orders | Revenue: $3,847.92

BY STATUS:
- Processing: 8 orders ($1,234.50)
- Pending Payment: 2 orders ($189.00)
- On Hold: 1 order ($79.99)
- Completed: 12 orders ($2,344.43)

TOP ORDERS:
1. Order #1823 - $459.99 (Processing)
2. Order #1821 - $389.00 (Completed)
3. Order #1819 - $234.50 (Processing)

Need me to process any specific orders?
```

## 🎨 Theme & Template Editing

### Quick Template Fixes
```
Human: There's a typo in my header - "Wellcome" should be "Welcome"

Claude: I'll fix that typo in your header template.

*[Locating header template...]*
Found in: /themes/your-theme/header.php

*[Creating backup...]*
Backup saved: header.php.backup-2024-01-19-143022

*[Fixing typo...]*
Found "Wellcome" on line 47
Replaced with "Welcome"

✅ Fixed! The typo has been corrected.
   - File: header.php
   - Line: 47
   - Backup available if needed
   - Clear your cache to see changes
```

### CSS Updates
```
Human: Make all buttons blue instead of green

Claude: I'll update your button colors from green to blue.

*[Scanning stylesheets...]*
Found button styles in: style.css

*[Creating backup...]*
Backup: style.css.backup-2024-01-19-144105

*[Updating colors...]*
Changed:
- Primary button: #28a745 → #007bff
- Button hover: #218838 → #0056b3
- Button active: #1e7e34 → #004085

✅ Updated all button colors to blue
   - 12 color values changed
   - Consistent blue theme applied
   - Preview in customizer to verify
```

## 🖼️ Media Management

### Bulk Image Upload
```
Human: I have 20 product images to upload, they're all in my downloads folder

Claude: I'll help you upload those product images. Please drag and drop them into this chat or specify their location.