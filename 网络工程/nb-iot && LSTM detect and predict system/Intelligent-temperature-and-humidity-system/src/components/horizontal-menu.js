const menuItems = [{
        id: 1,
        label: 'Dashboard',
        icon: 'ti-home',
        link: '/'
    },
    {
        id: 2,
        label: 'UI Elements',
        icon: 'ti-package',
        subItems: [{
                id: 3,
                label: 'Alerts',
                link: '/ui/alerts'
            },
            {
                id: 4,
                label: 'Buttons',
                link: '/ui/buttons'
            },
            {
                id: 5,
                label: 'Cards',
                link: '/ui/cards'
            },
            {
                id: 6,
                label: 'Carousel',
                link: '/ui/carousel'
            },
            {
                id: 7,
                label: 'Dropdowns',
                link: '/ui/dropdowns'
            },
            {
                id: 8,
                label: 'Grid',
                link: '/ui/grid'
            },
            {
                id: 9,
                label: 'Images',
                link: '/ui/images'
            }, {
                id: 10,
                label: 'Modals',
                link: '/ui/modals'
            }, {
                id: 11,
                label: 'Range Slider',
                link: '/ui/rangeslider'
            },
            {
                id: 12,
                label: 'Progress Bars',
                link: '/ui/progressbar'
            }, {
                id: 13,
                label: 'Sweet-Alert',
                link: '/ui/sweetalert'
            }, {
                id: 14,
                label: 'Tabs & Accordions',
                link: '/ui/tabs'
            }, {
                id: 15,
                label: 'Typography',
                link: '/ui/typography'
            }, {
                id: 16,
                label: 'Video',
                link: '/ui/video'
            }, {
                id: 17,
                label: 'General',
                link: '/ui/general'
            }, {
                id: 18,
                label: 'Colors',
                link: '/ui/colors'
            }, {
                id: 19,
                label: 'Rating',
                link: '/ui/rating'
            }
        ]
    },
    {
        id: 20,
        label: 'Components',
        icon: 'ti-harddrives',
        subItems: [
            {
                id: 21,
                label: 'Email',
                subItems: [{
                        id: 22,
                        label: 'Inbox',
                        link: '/email/inbox'
                    },
                    {
                        id: 23,
                        label: 'Email Read',
                        link: '/email/read-email'
                    },
                    {
                        id: 24,
                        label: 'Email Compose',
                        link: '/email/compose'
                    }
                ]
            },
            {
                id: 25,
                label: 'Calendar',
                link: '/calendar'
            },
            {
                id: 26,
                label: 'Forms',
                subItems: [{
                        id: 27,
                        label: 'Form Elements',
                        link: '/form/elements'
                    },
                    {
                        id: 28,
                        label: 'Form Validation',
                        link: '/form/validation'
                    },
                    {
                        id: 29,
                        label: 'Form Advanced',
                        link: '/form/advanced'
                    },
                    {
                        id: 30,
                        label: 'Form Editors',
                        link: '/form/editor'
                    },
                    {
                        id: 31,
                        label: 'Form File Upload',
                        link: '/form/uploads'
                    },
                    {
                        id: 32,
                        label: 'Form Repeater',
                        link: '/form/repeater'
                    },
                    {
                        id: 33,
                        label: 'Form Wizard',
                        link: '/form/wizard'
                    },
                    {
                        id: 34,
                        label: 'Form Mask',
                        link: '/form/mask'
                    }
                ]
            },
            {
                id: 35,
                label: 'Charts',
                subItems: [{
                        id: 36,
                        label: "Chartist Chart",
                        link: '/charts/chartist'
                    },
                    {
                        id: 37,
                        label: "Chartjs Chart",
                        link: '/charts/chartjs'
                    },
                    {
                        id: 38,
                        label: "Apex Chart",
                        link: '/charts/apex'
                    },
                ]
            },
            {
                id: 39,
                label: 'Tables',
                icon: 'ti-view-grid',
                subItems: [{
                        id: 40,
                        label: 'Basic Tables',
                        link: '/tables/basic'
                    },
                    {
                        id: 41,
                        label: 'Advanced Table',
                        link: '/tables/advanced'
                    },
                ]
            },
            {
                id: 42,
                label: "Icons",
                icon: 'ti-face-smile',
                subItems: [{
                        id: 43,
                        label: 'Material Design',
                        link: '/icons/material'
                    },
                    {
                        id: 44,
                        label: "Font Awesome",
                        link: '/icons/fontawesome'
                    },
                    {
                        id: 45,
                        label: "Ion Icons",
                        link: '/icons/ion'
                    },
                    {
                        id: 46,
                        label: "Themify Icons",
                        link: '/icons/themify'
                    },
                    {
                        id: 47,
                        label: "Dripicons",
                        link: '/icons/dripicons'
                    },
                    {
                        id: 48,
                        label: "Typicons Icons",
                        link: '/icons/typicons'
                    },
                ]
            },
            {
                id: 50,
                label: "Google Map",
                link: '/maps/google',
            },
        ]
    },
    {
        id: 52,
        label: 'Authentication',
        icon: 'ti-archive',
        subItems: [{
                id: 53,
                label: 'Login 1',
                link: '/pages/login-1'
            },
            {
                id: 54,
                label: 'Login 2',
                link: '/pages/login-2'
            },
            {
                id: 55,
                label: 'Register 1',
                link: '/pages/register-1'
            },
            {
                id: 56,
                label: 'Register 2',
                link: '/pages/register-2'
            },
            {
                id: 57,
                label: 'Recover Password 1',
                link: '/pages/recoverpwd-1'
            },
            {
                id: 58,
                label: 'Recover Password 2',
                link: '/pages/recoverpwd-2'
            },
            {
                id: 59,
                label: 'Lock Screen 1',
                link: '/pages/lock-screen1'
            },
            {
                id: 60,
                label: 'Lock Screen 2',
                link: '/pages/lock-screen2'
            }
        ]
    },
    {
        id: 61,
        label: 'Extra Pages',
        icon: 'ti-support',
        subItems: [{
                id: 62,
                label: 'Timeline',
                link: '/pages/timeline'
            },
            {
                id: 63,
                label: 'Invoice',
                link: '/pages/invoice'
            },
            {
                id: 64,
                label: 'Directory',
                link: '/pages/directory'
            },
            {
                id: 65,
                label: 'Blank Page',
                link: '/pages/blank-page'
            },
            {
                id: 66,
                label: 'Error 404',
                link: '/pages/404'
            },
            {
                id: 67,
                label: 'Error 500',
                link: '/pages/500'
            },
            {
                id: 68,
                label: 'Pricing',
                link: '/pages/pricing'
            },
            {
                id: 69,
                label: 'Maintenance',
                link: '/pages/maintenance'
            },
            {
                id: 70,
                label: 'FAQs',
                link: '/pages/faqs'
            }
        ]
    },
    {
        id: 71,
        label: 'Email Templates',
        icon: 'ti-bookmark-alt',
        subItems: [{
                id: 72,
                label: 'Basic Action Email',
                link: '/email-template/basic'
            },
            {
                id: 73,
                label: 'Alert Email',
                link: '/email-template/alert'
            },
            {
                id: 74,
                label: 'Billing Email',
                link: '/email-template/billing'
            },
        ]
    }
];

export {
    menuItems
};