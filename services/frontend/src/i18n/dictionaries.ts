export const LANGS = ["en", "ar", "he"] as const;
export type Lang = (typeof LANGS)[number];
export const RTL: Lang[] = ["ar", "he"];

// Arabic and Hebrew strings should be reviewed by a native speaker.
const en = {
  brandSubtitle: "Luxury Fragrance Admin",
  nav: {
    dashboard: "Dashboard", products: "Products", categories: "Categories", orders: "Orders", customers: "Customers",
    loyalty: "Loyalty", branches: "Branches", staff: "Staff", notifications: "Notifications", settings: "Settings", logout: "Logout",
  },
  role: { admin: "Admin" },
  greeting: { morning: "Morning", afternoon: "Afternoon", evening: "Evening" },
  dashboard: {
    subtitle: "Here's what's happening at MAD PERFUME today.",
    totalCustomers: "Total Customers", totalProducts: "Total Products", totalOrders: "Total Orders", pointsIssued: "Points Issued",
    stable: "Stable", lifetime: "Lifetime",
    recentOrders: "Recent Orders", viewAll: "View All", orderId: "Order ID", customer: "Customer", status: "Status", total: "Total",
    noOrders: "No orders yet.",
    loyaltyActivity: "Loyalty Activity", noActivity: "No loyalty activity yet.", pts: "pts",
    loadError: "Couldn't load dashboard data. Please refresh.",
  },
  categories: {
    title: "Categories", subtitle: "Manage fragrance collections and olfactory classifications.", add: "Add Category",
    total: "Total Categories", management: "Management Interface",
    image: "Image", name: "Category Name", type: "Type", products: "Products", actions: "Actions", items: "Items",
    empty: "No categories yet. Add your first one.", loadError: "Couldn't load categories. Please refresh.",
    showing: "Showing {from} to {to} of {total} categories",
    newTitle: "Add New Category", editTitle: "Edit Category", modalSubtitle: "Define a new segment for your inventory",
    imageLabel: "Category Showcase Image", upload: "Click to upload high-res image", uploadHint: "PNG, JPG or WebP (max. 10MB)",
    namePlaceholder: "e.g., Midnight Collection", typeLabel: "Category Type", selectType: "Select Type",
    description: "Brief Description", descriptionPlaceholder: "Describe the essence and core scent profiles of this category...",
    discard: "Discard", save: "Save Category", saving: "Saving…", edit: "Edit", delete: "Delete",
    confirmDelete: "Delete this category?", saveError: "Unable to save the category.", deleteError: "Unable to delete the category.",
    types: { classic: "Classic", premium: "Premium", exotic: "Exotic", seasonal: "Seasonal", niche: "Niche" },
  },
};

export type Dictionary = typeof en;

const ar: Dictionary = {
  brandSubtitle: "إدارة العطور الفاخرة",
  nav: {
    dashboard: "لوحة التحكم", products: "المنتجات", categories: "الفئات", orders: "الطلبات", customers: "العملاء",
    loyalty: "الولاء", branches: "الفروع", staff: "الموظفون", notifications: "الإشعارات", settings: "الإعدادات", logout: "تسجيل الخروج",
  },
  role: { admin: "مسؤول" },
  greeting: { morning: "صباح الخير", afternoon: "مساء الخير", evening: "مساء الخير" },
  dashboard: {
    subtitle: "إليك ما يحدث في MAD PERFUME اليوم.",
    totalCustomers: "إجمالي العملاء", totalProducts: "إجمالي المنتجات", totalOrders: "إجمالي الطلبات", pointsIssued: "النقاط الممنوحة",
    stable: "مستقر", lifetime: "مدى الحياة",
    recentOrders: "أحدث الطلبات", viewAll: "عرض الكل", orderId: "رقم الطلب", customer: "العميل", status: "الحالة", total: "الإجمالي",
    noOrders: "لا توجد طلبات بعد.",
    loyaltyActivity: "نشاط الولاء", noActivity: "لا يوجد نشاط ولاء بعد.", pts: "نقطة",
    loadError: "تعذر تحميل بيانات لوحة التحكم. يرجى التحديث.",
  },
  categories: {
    title: "الفئات", subtitle: "إدارة مجموعات العطور والتصنيفات العطرية.", add: "إضافة فئة",
    total: "إجمالي الفئات", management: "واجهة الإدارة",
    image: "الصورة", name: "اسم الفئة", type: "النوع", products: "المنتجات", actions: "الإجراءات", items: "منتج",
    empty: "لا توجد فئات بعد. أضف أول فئة.", loadError: "تعذر تحميل الفئات. يرجى التحديث.",
    showing: "عرض {from} إلى {to} من {total} فئة",
    newTitle: "إضافة فئة جديدة", editTitle: "تعديل الفئة", modalSubtitle: "حدد قسماً جديداً لمخزونك",
    imageLabel: "صورة عرض الفئة", upload: "انقر لرفع صورة عالية الدقة", uploadHint: "PNG أو JPG أو WebP (بحد أقصى 10 ميغابايت)",
    namePlaceholder: "مثال: مجموعة منتصف الليل", typeLabel: "نوع الفئة", selectType: "اختر النوع",
    description: "وصف مختصر", descriptionPlaceholder: "صف جوهر هذه الفئة وملامحها العطرية الأساسية...",
    discard: "تجاهل", save: "حفظ الفئة", saving: "جارٍ الحفظ…", edit: "تعديل", delete: "حذف",
    confirmDelete: "هل تريد حذف هذه الفئة؟", saveError: "تعذر حفظ الفئة.", deleteError: "تعذر حذف الفئة.",
    types: { classic: "كلاسيكي", premium: "فاخر", exotic: "غريب", seasonal: "موسمي", niche: "حصري" },
  },
};

const he: Dictionary = {
  brandSubtitle: "ניהול בשמי יוקרה",
  nav: {
    dashboard: "לוח בקרה", products: "מוצרים", categories: "קטגוריות", orders: "הזמנות", customers: "לקוחות",
    loyalty: "נאמנות", branches: "סניפים", staff: "צוות", notifications: "התראות", settings: "הגדרות", logout: "התנתקות",
  },
  role: { admin: "מנהל" },
  greeting: { morning: "בוקר טוב", afternoon: "צהריים טובים", evening: "ערב טוב" },
  dashboard: {
    subtitle: "הנה מה שקורה היום ב-MAD PERFUME.",
    totalCustomers: "סה״כ לקוחות", totalProducts: "סה״כ מוצרים", totalOrders: "סה״כ הזמנות", pointsIssued: "נקודות שהונפקו",
    stable: "יציב", lifetime: "מצטבר",
    recentOrders: "הזמנות אחרונות", viewAll: "הצג הכל", orderId: "מספר הזמנה", customer: "לקוח", status: "סטטוס", total: "סה״כ",
    noOrders: "אין הזמנות עדיין.",
    loyaltyActivity: "פעילות נאמנות", noActivity: "אין פעילות נאמנות עדיין.", pts: "נק׳",
    loadError: "לא ניתן לטעון את נתוני לוח הבקרה. נא לרענן.",
  },
  categories: {
    title: "קטגוריות", subtitle: "ניהול קולקציות בשמים וסיווגים ריחניים.", add: "הוספת קטגוריה",
    total: "סה״כ קטגוריות", management: "ממשק ניהול",
    image: "תמונה", name: "שם הקטגוריה", type: "סוג", products: "מוצרים", actions: "פעולות", items: "פריטים",
    empty: "אין קטגוריות עדיין. הוסיפו את הראשונה.", loadError: "לא ניתן לטעון קטגוריות. נא לרענן.",
    showing: "מציג {from} עד {to} מתוך {total} קטגוריות",
    newTitle: "הוספת קטגוריה חדשה", editTitle: "עריכת קטגוריה", modalSubtitle: "הגדירו פלח חדש למלאי שלכם",
    imageLabel: "תמונת תצוגה לקטגוריה", upload: "לחצו להעלאת תמונה באיכות גבוהה", uploadHint: "PNG, JPG או WebP (עד 10MB)",
    namePlaceholder: "לדוגמה: קולקציית חצות", typeLabel: "סוג הקטגוריה", selectType: "בחרו סוג",
    description: "תיאור קצר", descriptionPlaceholder: "תארו את המהות ואת פרופילי הריח של קטגוריה זו...",
    discard: "ביטול", save: "שמירת קטגוריה", saving: "שומר…", edit: "עריכה", delete: "מחיקה",
    confirmDelete: "למחוק את הקטגוריה?", saveError: "לא ניתן לשמור את הקטגוריה.", deleteError: "לא ניתן למחוק את הקטגוריה.",
    types: { classic: "קלאסי", premium: "פרימיום", exotic: "אקזוטי", seasonal: "עונתי", niche: "נישה" },
  },
};

export const dictionaries: Record<Lang, Dictionary> = { en, ar, he };
