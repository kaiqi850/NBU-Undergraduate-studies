import store from '@/state/store'

export default [{
        path: '/',
        meta: {
            authRequired: true
        },
        name: 'home',
        component: () => import('./views/home'),
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('./views/account/login'),
        meta: {
            beforeResolve(routeTo, routeFrom, next) {
                // If the user is already logged in
                if (store.getters['auth/loggedIn']) {
                    // Redirect to the home page instead
                    next({
                        name: 'home'
                    })
                } else {
                    // Continue to the login page
                    next()
                }
            },
        },
    },
    {
        path: '/register',
        name: 'register',
        component: () => import('./views/account/register'),
        meta: {
            beforeResolve(routeTo, routeFrom, next) {
                // If the user is already logged in
                if (store.getters['auth/loggedIn']) {
                    // Redirect to the home page instead
                    next({
                        name: 'home'
                    })
                } else {
                    // Continue to the login page
                    next()
                }
            },
        },
    },
    {
        path: '/forgot-password',
        name: 'forgot-password',
        component: () => import('./views/account/forgot-password'),
        meta: {
            beforeResolve(routeTo, routeFrom, next) {
                // If the user is already logged in
                if (store.getters['auth/loggedIn']) {
                    // Redirect to the home page instead
                    next({
                        name: 'home'
                    })
                } else {
                    // Continue to the login page
                    next()
                }
            },
        },
    },
    {
        path: '/logout',
        name: 'logout',
        meta: {
            authRequired: true,
            beforeResolve(routeTo, routeFrom, next) {
                if (process.env.VUE_APP_DEFAULT_AUTH === "firebase") {
                    store.dispatch('auth/logOut')
                } else {
                    store.dispatch('authfack/logout')
                }
                const authRequiredOnPreviousRoute = routeFrom.matched.some(
                    (route) => route.push('/login')
                )
                // Navigate back to previous page, or home as a fallback
                next(authRequiredOnPreviousRoute ? {
                    name: 'default'
                } : {
                    ...routeFrom
                })
            },
        },
    },
    {
        path: '/management',
        name: 'Management',
        component: () => import('./views/management/index'),
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/analysis',
        name: 'Analysis',
        component: () => import('./views/analysis/index'),
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/histroydata',
        name: 'HistroyData',
        component: () => import('./views/histroy/index'),
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/abouts',
        name: 'About',
        component: () => import('./views/abouts/index'),
        meta: {
            authRequired: true,
        },
    },
]