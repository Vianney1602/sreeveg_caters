# Architecture & Data Flow Diagrams

## 1. ADMIN DASHBOARD ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                     AdminDashboard Component                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  State Management (React Hooks)                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Menu Items, Orders, Customers, Stats                    │   │
│  │ activeTab, showAddForm                                   │   │
│  │ orderSortBy, customerSortBy, customerFilterName         │   │
│  │ editingItem, editForm, newItem                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────┬──────────────┬─────────────┬──────────────┐    │
│  │  Overview   │    Menu      │   Orders    │  Customers   │    │
│  │    Tab      │   Management │     Tab     │     Tab      │    │
│  │             │     Tab      │             │              │    │
│  └─────────────┼──────────────┼─────────────┼──────────────┘    │
│                │              │             │                   │
│                ↓              ↓             ↓                   │
│         ┌─────────────────────────────────────────┐             │
│         │  Functions & Event Handlers             │             │
│         ├─────────────────────────────────────────┤             │
│         │ • handleAddItem()        (Add/Edit)     │             │
│         │ • deleteItem()           (Delete)       │             │
│         │ • toggleAvailability()   (Toggle)       │             │
│         │ • getSortedOrders()      (Sort orders) │             │
│         │ • getFilteredAndSorted() (Filter/Sort) │             │
│         └─────────────────────────────────────────┘             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               API Communication (Axios)                    │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ GET /api/menu               → Fetch menu items            │ │
│  │ POST /api/menu              → Add new item               │ │
│  │ PUT /api/menu/{id}          → Update item                │ │
│  │ DELETE /api/menu/{id}       → Delete item                │ │
│  │ POST /api/uploads/image     → Upload image               │ │
│  │ GET /api/orders             → Fetch orders               │ │
│  │ PUT /api/orders/status/{id} → Update status              │ │
│  │ GET /api/customers          → Fetch customers            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            Real-time Updates (Socket.IO)                  │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ • menu_item_added     → New item notification            │ │
│  │ • menu_item_updated   → Update notification              │ │
│  │ • menu_item_deleted   → Delete notification              │ │
│  │ • order_status_changed → Status change notification      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. MENU MANAGEMENT FLOW

```
                    Menu Management Tab
                            |
                    ┌───────┴───────┐
                    ↓               ↓
            ┌──────────────┐  ┌──────────────┐
            │  Add Button  │  │  Edit Button │
            └──────┬───────┘  └───────┬──────┘
                   │                  │
         ┌─────────↓──────────────────↓──────────┐
         │     Show Add/Edit Form                │
         └─────────┬──────────────────┬──────────┘
                   │                  │
            ┌──────↓──────┐    ┌──────↓──────┐
            │  Fill Form  │    │ Auto-fill   │
            │  - Name     │    │ existing    │
            │  - Category │    │ values      │
            │  - Price    │    │             │
            │  - Desc     │    └──────┬──────┘
            │  - Image    │           │
            └──────┬──────┘           │
                   └─────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Image Selected? │
                    └────────┬────────┘
                             │
                   ┌─────────┴─────────┐
                   ↓                   ↓
            ┌─────────────┐   ┌──────────────┐
            │Yes: Upload  │   │No: Use existing
            │to Server    │   │or suggested  │
            └─────┬───────┘   └──────┬───────┘
                  │                  │
                  └────────┬─────────┘
                           ↓
                  ┌─────────────────┐
                  │  Show Preview   │
                  └─────────┬───────┘
                            ↓
                  ┌─────────────────┐
                  │ Submit Form     │
                  │ (Add/Update)    │
                  └─────────┬───────┘
                            ↓
         ┌──────────────────────────────────┐
         │  API Call (POST or PUT)          │
         │  - Include item data             │
         │  - Include image URL (if any)    │
         └──────────────┬───────────────────┘
                        ↓
         ┌──────────────────────────────────┐
         │  Server Response                 │
         ├──────────────┬───────────────────┤
         │ Success      │ Error             │
         │ ✅ Message   │ ❌ Alert message  │
         │ Close form   │ Form stays open   │
         │ Refresh list │                   │
         │ Socket update│                   │
         └──────────────┴───────────────────┘
                        ↓
         ┌──────────────────────────────────┐
         │  Real-time Broadcast              │
         │  - All clients notified           │
         │  - Other admins see change        │
         └──────────────────────────────────┘
```

---

## 3. DELETE OPERATION FLOW

```
                 Delete Button Click
                        |
                        ↓
         ┌─────────────────────────────┐
         │ Get Item Details            │
         │ (Name, ID, etc.)            │
         └────────────┬────────────────┘
                      ↓
         ┌─────────────────────────────┐
         │ Show Confirmation Dialog    │
         │ "Delete 'Item Name'?        │
         │  This cannot be undone."    │
         └────────────┬────────────────┘
                      │
            ┌─────────┴─────────┐
            ↓                   ↓
       ┌────────┐          ┌────────┐
       │ Cancel │          │ Confirm│
       └────┬───┘          └───┬────┘
            │                  ↓
            │         ┌────────────────────┐
            │         │ API DELETE call    │
            │         │ /api/menu/{id}     │
            │         └────────┬───────────┘
            │                  ↓
            │         ┌────────────────────┐
            │         │ Server Deletes:    │
            │         │ 1. DB record       │
            │         │ 2. Image file      │
            │         └────────┬───────────┘
            │                  ↓
            │         ┌────────────────────┐
            │         │ Success Response   │
            │         └────────┬───────────┘
            │                  ↓
            │         ┌────────────────────┐
            │         │ Frontend Actions:  │
            │         │ 1. Remove from UI  │
            │         │ 2. Show alert ✅   │
            │         │ 3. Close form      │
            │         │ 4. Socket update   │
            │         └────────────────────┘
            │
            └───────────────────┬──────────────┘
                                ↓
                        ┌────────────────┐
                        │ View Updated   │
                        │ Menu List      │
                        └────────────────┘
```

---

## 4. SORTING & FILTERING FLOW

```
                    Orders Tab / Customers Tab
                              |
                ┌─────────────┴─────────────┐
                ↓                           ↓
         ┌─────────────┐          ┌─────────────────┐
         │ Sort Select │          │ Search Input    │
         └────────┬────┘          │ (Customers only)│
                  │               └────────┬────────┘
                  │                        │
    ┌─────────────┴──────────────┐         │
    │ User Selects Sort Option   │         │
    │ - Newest First             │    ┌────┴─────────────────┐
    │ - Oldest First             │    │ User Types Search    │
    │ - Name A-Z                 │    │ (name or email)      │
    │ - Name Z-A                 │    └────────┬─────────────┘
    └────────────┬───────────────┘             │
                 │                             │
      ┌──────────↓──────────────────────────────↓──────────┐
      │ State Update (Immutable)                           │
      │ setOrderSortBy(value) or setCustomerFilterName()  │
      └──────────────┬───────────────────────────────────┘
                     │
      ┌──────────────↓────────────────────────────────────┐
      │ Call Sorting/Filtering Function                  │
      │ - getSortedOrders() or                          │
      │ - getFilteredAndSortedCustomers()               │
      └──────────────┬────────────────────────────────────┘
                     │
      ┌──────────────↓────────────────────────────────────┐
      │ Processing (Client-side, No API Call!)           │
      │                                                   │
      │ For Sorting:                                      │
      │  [...array].sort((a, b) => comparison)          │
      │                                                   │
      │ For Filtering:                                    │
      │  array.filter(item => match(searchTerm))        │
      │                                                   │
      │ Combined:                                         │
      │  Filter first, then sort results                │
      └──────────────┬────────────────────────────────────┘
                     │
      ┌──────────────↓────────────────────────────────────┐
      │ React Re-render                                   │
      │ (Only affected components re-render)             │
      └──────────────┬────────────────────────────────────┘
                     │
      ┌──────────────↓────────────────────────────────────┐
      │ Display Results                                   │
      │ - Sorted orders                                   │
      │ - Filtered customers                             │
      │ - Updated count                                   │
      │ - Empty state (if no results)                     │
      └──────────────┬────────────────────────────────────┘
                     │
      ┌──────────────↓────────────────────────────────────┐
      │ Show Results                                      │
      │ - List updates instantly                         │
      │ - No page reload                                  │
      │ - Fast and responsive                            │
      └──────────────────────────────────────────────────┘
```

---

## 5. IMAGE UPLOAD FLOW

```
                  User Selects Image File
                          |
                          ↓
              ┌─────────────────────────┐
              │ Validate File           │
              │ - Type: jpg, png, gif   │
              │ - Size: < 5MB           │
              └────────────┬────────────┘
                           │
                    ┌──────┴──────┐
                    ↓             ↓
            ┌─────────────┐  ┌────────────┐
            │ Valid       │  │ Invalid    │
            └──────┬──────┘  │ Show error │
                   │         └────────────┘
                   ↓
        ┌─────────────────────────┐
        │ Show Image Preview      │
        │ (URL.createObjectURL)   │
        └────────────┬────────────┘
                     ↓
        ┌─────────────────────────┐
        │ User Submits Form       │
        │ (handleAddItem)         │
        └────────────┬────────────┘
                     ↓
        ┌─────────────────────────────────┐
        │ Create FormData                 │
        │ - Append file as 'image'        │
        └────────────┬────────────────────┘
                     ↓
        ┌─────────────────────────────────┐
        │ POST /api/uploads/image         │
        │ Content-Type: multipart/form    │
        └────────────┬────────────────────┘
                     ↓
        ┌─────────────────────────────────┐
        │ Backend Processing              │
        │ - Validate file again           │
        │ - Secure filename               │
        │ - Save to /static/uploads/      │
        │ - Generate unique name if exists│
        └────────────┬────────────────────┘
                     │
            ┌────────┴────────┐
            ↓                 ↓
     ┌────────────┐    ┌────────────┐
     │ Success    │    │ Fail       │
     │Return URL  │    │Show error  │
     └─────┬──────┘    │Continue    │
           │           │without img │
           ↓           └────────────┘
     ┌────────────────────────┐
     │ Add URL to POST/PUT    │
     │ Menu Item Request      │
     └──────────┬─────────────┘
                ↓
     ┌────────────────────────┐
     │ Send API Request with  │
     │ - Item data            │
     │ - Image URL            │
     └──────────┬─────────────┘
                ↓
     ┌────────────────────────┐
     │ Save to Database       │
     │ - Store image URL      │
     │ - Link to menu item    │
     └──────────┬─────────────┘
                ↓
     ┌────────────────────────┐
     │ Success Response       │
     │ Display image in list  │
     └────────────────────────┘
```

---

## 6. CUSTOMER SEARCH ALGORITHM

```
                  Input: Search Term
                          |
                          ↓
     ┌────────────────────────────────────┐
     │ Convert to lowercase for comparison│
     │ searchTerm = userInput.lower()     │
     └────────────┬───────────────────────┘
                  │
     ┌────────────↓───────────────────────┐
     │ Iterate through all customers      │
     └────────────┬───────────────────────┘
                  │
          ┌───────↓────────┐
          ↓                ↓
     ┌──────────┐    ┌──────────┐
     │ Full Name│    │   Email  │
     │          │    │          │
     │Check if: │    │Check if: │
     │name.incl-│    │email.incl-
     │(search)  │    │(search)  │
     └─────┬────┘    └────┬─────┘
           │              │
        ┌──┴──────────────┴──┐
        ↓                     ↓
    ┌────────┐          ┌────────────┐
    │ Match  │          │ No Match   │
    │ Found  │          │ Skip item  │
    └────┬───┘          └────────────┘
         │
         ↓
    ┌────────────────────┐
    │ Add to Results     │
    │ (Filtered Array)   │
    └────────┬───────────┘
             │
     ┌───────↓────────────────────┐
     │ Continue with next customer│
     └───────┬────────────────────┘
             │
     ┌───────↓────────────────────────────┐
     │ After filtering all customers:     │
     │ Return filtered array              │
     └───────┬────────────────────────────┘
             │
     ┌───────↓────────────────────────────┐
     │ Check if results exist:            │
     │ - If YES: Display filtered list    │
     │ - If NO:  Show "No results" msg    │
     └────────────────────────────────────┘
```

---

## 7. STATE MANAGEMENT DIAGRAM

```
┌────────────────────────────────────────────────────────────┐
│                AdminDashboard State (useState)             │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Tab Navigation                                       │   │
│ ├──────────────────────────────────────────────────────┤   │
│ │ activeTab: 'overview'|'menu'|'orders'|'customers'    │   │
│ │           |'database'                                │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Data from API                                        │   │
│ ├──────────────────────────────────────────────────────┤   │
│ │ menuItems: Array<MenuItem>                           │   │
│ │ orders: Array<Order>                                 │   │
│ │ customers: Array<Customer>                           │   │
│ │ stats: { totalOrders, pending, revenue, ... }       │   │
│ │ eventTypes: Array<EventType>                         │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Menu Management                                      │   │
│ ├──────────────────────────────────────────────────────┤   │
│ │ showAddForm: boolean                                 │   │
│ │ newItem: {name, category, price, description, image}│   │
│ │ editingItem: null | {id, name, category, ...}       │   │
│ │ editForm: {name, category, price, description, img} │   │
│ │ newImageFile: null | File                            │   │
│ │ editImageFile: null | File                           │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Sorting & Filtering                                  │   │
│ ├──────────────────────────────────────────────────────┤   │
│ │ orderSortBy: 'date-desc'|'date-asc'|'name-asc'       │   │
│ │            |'name-desc'                              │   │
│ │ customerSortBy: 'date-desc'|'date-asc'|'name-asc'    │   │
│ │               |'name-desc'                           │   │
│ │ customerFilterName: string (search term)             │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ UI State                                             │   │
│ ├──────────────────────────────────────────────────────┤   │
│ │ expandedOrderId: null | number (order details)       │   │
│ │ loading: boolean                                     │   │
│ │ error: string                                        │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                             │
└────────────────────────────────────────────────────────────┘

Flow:
  State Change → Function Call → Processing → Re-render → UI Update
```

---

## 8. API REQUEST/RESPONSE CYCLE

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  User Action (click, type, submit)                              │
│              ↓                                                    │
│  State Update (setState)                                        │
│              ↓                                                    │
│  Function Call (handleAdd, delete, etc.)                        │
│              ↓                                                    │
│  Axios HTTP Request                                             │
│  ┌──────────────────────────────────────┐                       │
│  │ POST /api/menu                       │                       │
│  │ Headers: Content-Type: application.. │                       │
│  │ Body: {item_name, category, price...}│                       │
│  └────────────────┬─────────────────────┘                       │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (Flask)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Route Handler: @menu_bp.route("/", methods=["POST"])           │
│              ↓                                                    │
│  Validate Request:                                              │
│  - Check content type                                           │
│  - Validate required fields                                     │
│              ↓                                                    │
│  Database Operation:                                            │
│  - Create MenuItem instance                                     │
│  - db.session.add(item)                                         │
│  - db.session.commit()                                          │
│              ↓                                                    │
│  Socket.IO Broadcast:                                           │
│  - socketio.emit('menu_item_added', {...})                      │
│              ↓                                                    │
│  Return Response:                                               │
│  - Status: 200 OK                                               │
│  - Body: {message: "Item Added", item_id: 123}                  │
│                                                                   │
└───────────────────┬──────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Response Received:                                             │
│  ┌──────────────────────────────────┐                           │
│  │ .then(response => {              │                           │
│  │   console.log(response.data)     │                           │
│  │   setMenuItems([...])            │                           │
│  │   setShowAddForm(false)           │                           │
│  │   alert("Success!")              │                           │
│  │ })                               │                           │
│  └──────────────────────────────────┘                           │
│              ↓                                                    │
│  State Update (setMenuItems, etc.)                              │
│              ↓                                                    │
│  React Re-render                                                │
│              ↓                                                    │
│  UI Updated with New Data                                       │
│              ↓                                                    │
│  User Sees Changes                                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. RESPONSIVE DESIGN BREAKPOINTS

```
Desktop (> 1024px)
┌──────────────────────────────────────────────────────┐
│ Header (Full Width)                                  │
├─────────┬──────────┬──────────┬─────────┬────────────┤
│Overview │ Menu     │ Orders   │Customer │Database    │
│         │Management│          │ s       │            │
├──────────────────────────────────────────────────────┤
│ Content Area (Full Width)                            │
│                                                       │
│ Orders Header:                                        │
│ ┌──────────────────────┐  ┌──────────────────────┐  │
│ │ All Orders (15)      │  │ Sort by: [Newest ▼] │  │
│ └──────────────────────┘  └──────────────────────┘  │
│                                                       │
└──────────────────────────────────────────────────────┘


Tablet (768px - 1024px)
┌────────────────────────────────────────┐
│ Header (Full Width)                    │
├────────┬──────┬────────┬────────┬──────┤
│Overview│ Menu │ Orders │Cust.  │ DB   │
├────────────────────────────────────────┤
│ Content Area                           │
│                                        │
│ ┌──────────────────────────────────┐  │
│ │ All Orders (15)                  │  │
│ │ Sort by: [Newest ▼]             │  │
│ └──────────────────────────────────┘  │
│                                        │
└────────────────────────────────────────┘


Mobile (< 768px)
┌──────────────────┐
│ Header           │
├──────────────────┤
│ Overview         │ ← Vertical tabs
│ Menu Management  │
│ Orders           │
│ Customers        │
│ Database         │
├──────────────────┤
│ Content Area     │
│                  │
│ All Orders (15)  │
│                  │
│ ┌──────────────┐ │
│ │Sort by:      │ │ ← Full width
│ │[Newest ▼]    │ │
│ └──────────────┘ │
│                  │
└──────────────────┘
```

---

## 10. ERROR HANDLING FLOW

```
                    API Call Made
                        |
                        ↓
         ┌──────────────────────────┐
         │ Request Sent to Server   │
         └────────────┬─────────────┘
                      │
              ┌───────┴────────┐
              ↓                ↓
         ┌────────┐      ┌─────────┐
         │Success │      │ Error   │
         │(2xx)   │      │(4xx/5xx)│
         └────┬───┘      └────┬────┘
              │               │
         ┌────↓─────┐    ┌────↓──────────┐
         │.then()   │    │.catch()       │
         │Process   │    │Handle Error   │
         │data      │    │- Log error    │
         │Update UI │    │- Show message │
         └──────────┘    └───┬──────────┘
                             │
                    ┌────────↓─────────┐
                    │ User Sees Alert  │
                    │ with error details│
                    └──────────────────┘

Error Messages:
┌─────────────────────────────────────────┐
│ ❌ Failed to save item                  │
│    Error details from server            │
│    [OK]                                 │
└─────────────────────────────────────────┘

OR (for detailed errors):
┌─────────────────────────────────────────┐
│ ❌ Image upload failed.                 │
│    Item will be saved without image.    │
│    [OK]                                 │
└─────────────────────────────────────────┘
```

---

This comprehensive diagram set shows how all components interact and flow data through the system.
