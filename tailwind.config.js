/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [],
    purge:[
      './routes/templates/*.html',
      './routes/templates/routes/*.html',
      './routes/templates/registration/*.html',
      './routes/templates/gameboard/*.html',
    ],
  theme: {
    extend: {},
  },
  plugins: [],
}

