 const menuItems = [{
         id: 1,
         label: "Main",
         isTitle: true
     },
     {
         id: 2,
         label: '系统主页',
         icon: 'ti-home',
         link: '/'
     },
     {
         id: 3,
         label: '设备管理',
         icon: 'ti-receipt',
         link: '/management'
     },
     {
        id: 4,
        label: '数据分析',
        icon: 'ti-pie-chart',
        link: '/analysis'
    },
    {
        id: 5,
        label: '历史数据',
        icon: 'ti-package',
        link: '/histroydata'
    },
    {
        id: 6,
        label: 'EXTRAS',
        isTitle: true
        
    },
    {
        id: 7,
        label: '关于我们',
        icon: 'ti-face-smile',
        link: '/abouts',
        badge: {
            variant: "primary",
            text: "2"
        },
    },


    //  {
    //      id: 4,
    //      label: 'Email',
    //      icon: 'ti-email',
    //      subItems: [{
    //              id: 5,
    //              label: 'Inbox',
    //              link: '/email/inbox'
    //          },
    //          {
    //              id: 6,
    //              label: 'Email Read',
    //              link: '/email/read-email'
    //          },
    //          {
    //              id: 7,
    //              label: 'Email Compose',
    //              link: '/email/compose'
    //          }
    //      ]
    //  },

    /*
     {
         id: 8,
         label: 'Components',
         isTitle: true
     },
     {
         id: 9,
         label: 'UI Elements',
         icon: 'ti-package',
         subItems: [{
                 id: 10,
                 label: 'Alerts',
                 link: '/ui/alerts'
             },
             {
                 id: 11,
                 label: 'Buttons',
                 link: '/ui/buttons'
             },
             {
                 id: 12,
                 label: 'Cards',
                 link: '/ui/cards'
             },
             {
                 id: 13,
                 label: 'Carousel',
                 link: '/ui/carousel'
             },
             {
                 id: 14,
                 label: 'Dropdowns',
                 link: '/ui/dropdowns'
             },
             {
                 id: 15,
                 label: 'Grid',
                 link: '/ui/grid'
             },
             {
                 id: 16,
                 label: 'Images',
                 link: '/ui/images'
             }, {
                 id: 17,
                 label: 'Modals',
                 link: '/ui/modals'
             }, {
                 id: 18,
                 label: 'Range Slider',
                 link: '/ui/rangeslider'
             },
             {
                 id: 19,
                 label: 'Progress Bars',
                 link: '/ui/progressbar'
             }, {
                 id: 20,
                 label: 'Sweet-Alert',
                 link: '/ui/sweetalert'
             }, {
                 id: 21,
                 label: 'Tabs & Accordions',
                 link: '/ui/tabs'
             }, {
                 id: 22,
                 label: 'Typography',
                 link: '/ui/typography'
             }, {
                 id: 23,
                 label: 'Video',
                 link: '/ui/video'
             }, {
                 id: 24,
                 label: 'General',
                 link: '/ui/general'
             }, {
                 id: 25,
                 label: 'Colors',
                 link: '/ui/colors'
             }, {
                 id: 26,
                 label: 'Rating',
                 link: '/ui/rating'
             }
         ]
     },
     {
         id: 27,
         label: 'Forms',
         icon: 'ti-receipt',
         badge: {
             variant: 'success',
             text: '6'
         },
         subItems: [{
                 id: 28,
                 label: 'Form Elements',
                 link: '/form/elements'
             },
             {
                 id: 29,
                 label: 'Form Validation',
                 link: '/form/validation'
             },
             {
                 id: 30,
                 label: 'Form Advanced',
                 link: '/form/advanced'
             },
             {
                 id: 31,
                 label: 'Form Editors',
                 link: '/form/editor'
             },
             {
                 id: 32,
                 label: 'Form File Upload',
                 link: '/form/uploads'
             },
             {
                 id: 33,
                 label: 'Form Repeater',
                 link: '/form/repeater'
             },
             {
                 id: 34,
                 label: 'Form Wizard',
                 link: '/form/wizard'
             },
             {
                 id: 35,
                 label: 'Form Mask',
                 link: '/form/mask'
             }
         ]
     },
     {
         id: 36,
         label: 'Charts',
         icon: 'ti-pie-chart',
         subItems: [{
                 id: 37,
                 label: "Chartist Chart",
                 link: '/charts/chartist'
             },
             {
                 id: 38,
                 label: "Chartjs Chart",
                 link: '/charts/chartjs'
             },
             {
                 id: 39,
                 label: "Apex Chart",
                 link: '/charts/apex'
             },
             {
                 id: 39,
                 label: "E Chart",
                 link: '/charts/echart'
             },
         ]
     },
     {
         id: 40,
         label: 'Tables',
         icon: 'ti-view-grid',
         subItems: [{
                 id: 41,
                 label: 'Basic Tables',
                 link: '/tables/basic'
             },
             {
                 id: 42,
                 label: 'Advanced Table',
                 link: '/tables/advanced'
             },
         ]
     },
     {
         id: 43,
         label: "Icons",
         icon: 'ti-face-smile',
         subItems: [{
                 id: 44,
                 label: 'Material Design',
                 link: '/icons/material'
             },
             {
                 id: 45,
                 label: "Font Awesome",
                 link: '/icons/fontawesome'
             },
             {
                 id: 46,
                 label: "Ion Icons",
                 link: '/icons/ion'
             },
             {
                 id: 47,
                 label: "Themify Icons",
                 link: '/icons/themify'
             },
             {
                 id: 48,
                 label: "Dripicons",
                 link: '/icons/dripicons'
             },
             {
                 id: 49,
                 label: "Typicons Icons",
                 link: '/icons/typicons'
             },
         ]
     },
     {
         id: 50,
         label: "Google Map",
         icon: 'ti-location-pin',
         link: '/maps/google',
         badge: {
             variant: 'danger',
             text: '2'
         },
     },
     {
         id: 51,
         label: 'Extras',
         isTitle: true
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
     },
     {
         id: 75,
         label: "Multi Level",
         icon: "ti-more",
         subItems: [{
                 id: 76,
                 label: "Level 1.1",
                 link: "#",
                 parentId: 75
             },
             {
                 id: 77,
                 label: "Level 1.2",
                 parentId: 75,
                 subItems: [{
                         id: 78,
                         label: "Level 2.1",
                         link: "#",
                         parentId: 75
                     },
                     {
                         id: 79,
                         label: "Level 2.2",
                         link: "#",
                         parentId: 75
                     }
                 ]
             }
         ]
     }
     */
 ]

 export {
     menuItems
 };