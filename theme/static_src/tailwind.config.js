module.exports = {
    content: [
        // Templates en app theme
        '../templates/**/*.html',

        // Templates globales del proyecto
        '../../templates/**/*.html',

        // Templates en otras apps de Django
        '../../**/templates/**/*.html',

        // Flowbite JS (aunque no lo uses aquí, puedes dejarlo si tienes otros componentes)
        './node_modules/flowbite/**/*.js',
    ],
    theme: {
        extend: {
            keyframes: {
                'rent-loop': {
                    '0%': { transform: 'translateX(0)' },
                    '100%': { transform: 'translateX(-50%)' },
                },
                'purchase-loop': {
                    '0%': { transform: 'translateX(0)' },
                    '100%': { transform: 'translateX(-50%)' },
                },
            },
            animation: {
                'rent-loop': 'rent-loop 30s linear infinite',
                'purchase-loop': 'purchase-loop 30s linear infinite',
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('flowbite/plugin'),  
    ],
}
