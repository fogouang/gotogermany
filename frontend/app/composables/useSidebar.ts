export const useSidebar = () => {
  const collapsed = useCookie<boolean>("sidebar-collapsed", {
    default: () => false,
  });
  const mobileOpen = useState<boolean>("sidebar-mobile-open", () => false);

  const toggleCollapsed = () => {
    collapsed.value = !collapsed.value;
  };

  const openMobile = () => {
    mobileOpen.value = true;
  };

  return { collapsed, mobileOpen, toggleCollapsed, openMobile };
};