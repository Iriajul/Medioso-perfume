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
};

export const dictionaries: Record<Lang, Dictionary> = { en, ar, he };
