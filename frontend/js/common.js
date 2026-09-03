document.addEventListener("DOMContentLoaded", () => {
    injectSidebar();
});

const navItems = [
    { name: "Dashboard", url: "index.html", icon: `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>` },
    { name: "Production Intelligence", url: "production.html", icon: `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>` },
    { name: "Machine Health", url: "machines.html", icon: `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>` },
    { name: "Quality Inspection", url: "quality.html", icon: `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>` },
    { name: "AI Factory Copilot", url: "copilot.html", icon: `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>` },
    { name: "What-If Simulator", url: "simulator.html", icon: `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>` },
    { name: "Data", url: "data.html", icon: `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>` },
    { name: "About", url: "about.html", icon: `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>` }
];

function injectSidebar() {
    const mount = document.getElementById("sidebar-mount");
    if (!mount) return;
    
    // Check local storage for sidebar state (default to collapsed)
    const savedState = localStorage.getItem("sidebarState") || "collapsed";
    if (savedState === "expanded") {
        mount.classList.remove("collapsed");
        mount.classList.add("expanded");
    } else {
        mount.classList.remove("expanded");
        mount.classList.add("collapsed");
    }

    // Use pathname or fallback to index.html for root /
    let currentPath = window.location.pathname.split("/").pop();
    if (currentPath === "" || currentPath === "/") currentPath = "index.html";

    const navHtml = navItems.map(item => {
        const isActive = (item.url === currentPath) ? 'active' : '';
        if (item.name === "Data") {
            return `<div class="sidebar-divider"></div>
            <a href="${item.url}" class="nav-item ${isActive}" aria-label="${item.name}">
                ${item.icon}
                <span class="nav-label">${item.name} Management</span>
                <span class="nav-tooltip">${item.name} Management</span>
            </a>`;
        }
        return `
            <a href="${item.url}" class="nav-item ${isActive}" aria-label="${item.name}">
                ${item.icon}
                <span class="nav-label">${item.name}</span>
                <span class="nav-tooltip">${item.name}</span>
            </a>
        `;
    }).join("");

    mount.innerHTML = `
        <div class="sidebar-header">
            <div class="brand-container">
                <div class="brand-logo">LOOMIQ</div>
                <div class="brand-tagline">Manufacturing Intelligence</div>
            </div>
            <button class="menu-btn" id="menu-toggle" aria-label="Toggle Menu">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
            </button>
        </div>
        <nav class="nav-menu">
            ${navHtml}
        </nav>
    `;

    document.getElementById("menu-toggle").addEventListener("click", () => {
        const isCurrentlyExpanded = mount.classList.contains("expanded");
        
        if (isCurrentlyExpanded) {
            mount.classList.remove("expanded");
            mount.classList.add("collapsed");
            localStorage.setItem("sidebarState", "collapsed");
        } else {
            mount.classList.remove("collapsed");
            mount.classList.add("expanded");
            localStorage.setItem("sidebarState", "expanded");
        }
    });
}
