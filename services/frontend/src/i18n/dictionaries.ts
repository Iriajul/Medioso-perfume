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
  branches: {
    title: "Boutique Network", subtitle: "Manage your global presence and flagship boutiques with precision. Monitor locations, contacts, and performance metrics.",
    add: "Add New Branch", total: "Total Branches", thisQuarter: "+{n} this quarter", directory: "Branch Directory",
    name: "Branch Name", address: "Address", phone: "Contact Number", actions: "Actions",
    empty: "No branches yet. Add your first boutique.", loadError: "Couldn't load branches. Please refresh.",
    showing: "Showing {from} to {to} of {total} branches",
    newTitle: "Add New Branch", editTitle: "Edit Branch", modalSubtitle: "Register a new luxury location to the global MAD PERFUME network.",
    imageLabel: "Boutique Image Upload", upload: "Drag and drop high-resolution imagery", uploadHint: "PNG, JPG or WEBP up to 10MB (16:9 ratio recommended)", selectFiles: "Select Files",
    namePlaceholder: "e.g., Paris Flagship", fullAddress: "Full Address", addressPlaceholder: "Enter the complete street address, city, and postal code...",
    hours: "Operating Hours", weekdays: "Monday – Saturday", sunday: "Sunday & Holidays",
    location: "Map Location (optional)", latitude: "Latitude", longitude: "Longitude",
    save: "Add branch", update: "Save changes", saving: "Saving…", edit: "Edit", delete: "Delete",
    confirmDelete: "Delete this branch?", deleteError: "Unable to delete the branch.",
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
  branches: {
    title: "شبكة البوتيكات", subtitle: "أدر حضورك العالمي وبوتيكاتك الرئيسية بدقة. تابع المواقع وجهات الاتصال ومؤشرات الأداء.",
    add: "إضافة فرع جديد", total: "إجمالي الفروع", thisQuarter: "+{n} هذا الربع", directory: "دليل الفروع",
    name: "اسم الفرع", address: "العنوان", phone: "رقم الاتصال", actions: "الإجراءات",
    empty: "لا توجد فروع بعد. أضف أول بوتيك.", loadError: "تعذر تحميل الفروع. يرجى التحديث.",
    showing: "عرض {from} إلى {to} من {total} فرع",
    newTitle: "إضافة فرع جديد", editTitle: "تعديل الفرع", modalSubtitle: "سجّل موقعاً فاخراً جديداً في شبكة MAD PERFUME العالمية.",
    imageLabel: "رفع صورة البوتيك", upload: "اسحب وأفلت صوراً عالية الدقة", uploadHint: "PNG أو JPG أو WEBP حتى 10 ميغابايت (يُفضل 16:9)", selectFiles: "اختيار الملفات",
    namePlaceholder: "مثال: الفرع الرئيسي في باريس", fullAddress: "العنوان الكامل", addressPlaceholder: "أدخل عنوان الشارع والمدينة والرمز البريدي...",
    hours: "ساعات العمل", weekdays: "الاثنين – السبت", sunday: "الأحد والعطلات",
    location: "الموقع على الخريطة (اختياري)", latitude: "خط العرض", longitude: "خط الطول",
    save: "إضافة الفرع", update: "حفظ التغييرات", saving: "جارٍ الحفظ…", edit: "تعديل", delete: "حذف",
    confirmDelete: "هل تريد حذف هذا الفرع؟", deleteError: "تعذر حذف الفرع.",
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
  branches: {
    title: "רשת הבוטיקים", subtitle: "נהלו את הנוכחות הגלובלית ואת בוטיקי הדגל שלכם בדיוק. עקבו אחר מיקומים, אנשי קשר ומדדי ביצוע.",
    add: "הוספת סניף חדש", total: "סה״כ סניפים", thisQuarter: "+{n} ברבעון זה", directory: "מדריך סניפים",
    name: "שם הסניף", address: "כתובת", phone: "מספר טלפון", actions: "פעולות",
    empty: "אין סניפים עדיין. הוסיפו את הבוטיק הראשון.", loadError: "לא ניתן לטעון סניפים. נא לרענן.",
    showing: "מציג {from} עד {to} מתוך {total} סניפים",
    newTitle: "הוספת סניף חדש", editTitle: "עריכת סניף", modalSubtitle: "רשמו מיקום יוקרה חדש ברשת MAD PERFUME הגלובלית.",
    imageLabel: "העלאת תמונת בוטיק", upload: "גררו ושחררו תמונות באיכות גבוהה", uploadHint: "PNG, JPG או WEBP עד 10MB (מומלץ יחס 16:9)", selectFiles: "בחירת קבצים",
    namePlaceholder: "לדוגמה: סניף הדגל בפריז", fullAddress: "כתובת מלאה", addressPlaceholder: "הזינו כתובת רחוב מלאה, עיר ומיקוד...",
    hours: "שעות פעילות", weekdays: "שני – שבת", sunday: "ראשון וחגים",
    location: "מיקום במפה (אופציונלי)", latitude: "קו רוחב", longitude: "קו אורך",
    save: "הוספת סניף", update: "שמירת שינויים", saving: "שומר…", edit: "עריכה", delete: "מחיקה",
    confirmDelete: "למחוק את הסניף?", deleteError: "לא ניתן למחוק את הסניף.",
  },
};

export const dictionaries: Record<Lang, Dictionary> = { en, ar, he };
