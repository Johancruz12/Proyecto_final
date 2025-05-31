from flask import Flask, render_template_string, request, send_file
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from xhtml2pdf import pisa
import urllib.parse

app = Flask(__name__)

# CSS content
CSS = """
/* Import professional fonts */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

body {
  font-family: 'Roboto', 'Arial', sans-serif;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background: linear-gradient(135deg, #0a1d37, #1e3a8a, #2563eb);
  background-size: 400% 400%;
  animation: GradientAnimation 12s ease infinite;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #ffffff;
}

@keyframes GradientAnimation {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem 2.5rem;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
  animation: fadeIn 0.6s ease-out;
  color: #1e293b;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Headings */
h1 {
  text-align: center;
  color: #1e40af;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #1e40af;
  font-size: 1.8rem;
  font-weight: 500;
  margin: 1.5rem 0;
  text-align: center;
}

/* Sections */
section {
  margin-bottom: 2.5rem;
}

/* Form styling */
.calc-section {
  margin-bottom: 2.5rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

form {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-desc {
  font-size: 0.9rem;
  color: #475569;
  margin: 0;
  text-align: center;
}

label {
  font-weight: 500;
  font-size: 1.1rem;
  color: #1e293b;
  margin-bottom: 0.3rem;
}

input {
  padding: 0.9rem 1.2rem;
  font-size: 1rem;
  border: 2px solid #93c5fd;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: #ffffff;
}

input:focus {
  border-color: #2563eb;
  outline: none;
  box-shadow: 0 0 10px rgba(37, 99, 235, 0.3);
}

/* Error message styling */
.error-message {
  color: #dc2626;
  font-size: 0.9rem;
  margin-top: 0.3rem;
  margin-bottom: 0;
}

/* Button wrapper for centering */
.button-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

/* Buttons */
.btn-primary {
  background: linear-gradient(135deg, #2563eb, #1e40af);
  color: #ffffff;
  border: none;
  padding: 0.9rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 12px;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease, filter 0.3s ease;
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
  filter: brightness(1);
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.btn-primary:hover::before {
  left: 100%;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1e40af, #2563eb);
  transform: scale(1.05) translateY(-3px);
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.3);
  filter: brightness(1.1);
}

.btn-primary:active {
  transform: scale(0.98) translateY(0);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.2);
  filter: brightness(0.9);
}

.btn-primary:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.3), 0 6px 14px rgba(37, 99, 235, 0.4);
}

/* Guide button modifier */
.btn-primary.guia {
  background: linear-gradient(135deg, #16a34a, #15803d);
  box-shadow: 0 6px 14px rgba(22, 163, 74, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.2);
}

.btn-primary.guia:hover {
  background: linear-gradient(135deg, #15803d, #16a34a);
  transform: scale(1.05) translateY(-3px);
  box-shadow: 0 10px 20px rgba(22, 163, 74, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.3);
  filter: brightness(1.1);
}

.btn-primary.guia:active {
  transform: scale(0.98) translateY(0);
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.2);
  filter: brightness(0.9);
}

.btn-primary.guia:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.3), 0 6px 14px rgba(22, 163, 74, 0.4);
}

/* Back button style */
.btn-back {
  background: linear-gradient(135deg, #16a34a, #10b981);
  color: #ffffff;
  border: none;
  padding: 0.9rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 12px;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease, filter 0.3s ease;
  box-shadow: 0 6px 14px rgba(22, 163, 74, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
  filter: brightness(1);
}

.btn-back::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 259, 0.3), transparent);
  transition: left 0.5s ease;
}

.btn-back:hover::before {
  left: 100%;
}

.btn-back:hover {
  background: linear-gradient(135deg, #10b981, #16a34a);
  transform: scale(1.05) translateY(-3px);
  box-shadow: 0 10px 20px rgba(22, 163, 74, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.3);
  filter: brightness(1.1);
}

.btn-back:active {
  transform: scale(0.98) translateY(0);
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.2);
  filter: brightness(0.9);
}

.btn-back:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.3), 0 6px 14px rgba(22, 163, 74, 0.4);
}

/* Button icon styling */
.btn-icon {
  margin-right: 0.5rem;
  font-size: 1.2rem;
  vertical-align: middle;
  transition: transform 0.3s ease;
}

.btn-primary:hover .btn-icon,
.btn-back:hover .btn-icon {
  transform: scale(1.2);
}

/* Ripple effect for buttons */
.btn-ripple {
  position: relative;
  overflow: hidden;
}

.btn-ripple::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1);
  transform-origin: 50% 50%;
  animation: ripple 0.6s linear;
}

@keyframes ripple {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(50);
    opacity: 0;
  }
}

.btn-ripple:active::after {
  animation: ripple 0.6s linear;
}

/* Result page specific styles */
.result-container {
  text-align: center;
  padding: 2rem;
}

.result-container img {
  max-width: 100%;
  height: auto;
  margin: 1.5rem 0;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.mathjax {
  font-size: 1.2rem;
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f1f5f9;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  overflow-x: auto;
  white-space: nowrap;
  max-width: 100%;
  box-sizing: border-box;
  -webkit-overflow-scrolling: touch;
}

.mathjax * {
  white-space: nowrap;
}

/* GeoGebra container */
.geogebra-container {
  margin: 2rem auto;
  width: 100%;
  max-width: 800px;
  height: 450px;
  border: 2px solid #93c5fd;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.geogebra-container iframe {
  width: 100%;
  height: 100%;
  border: none;
}

/* Guide link section */
.info {
  text-align: center;
  margin-top: 2rem;
}

.info a {
  background: linear-gradient(135deg, #16a34a, #10b981);
  color: #ffffff;
  border: none;
  padding: 0.9rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 12px;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease, filter 0.3s ease;
  box-shadow: 0 6px 14px rgba(22, 163, 74, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
  filter: brightness(1);
}

.info a::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.info a:hover::before {
  left: 100%;
}

.info a:hover {
  background: linear-gradient(135deg, #10b981, #16a34a);
  transform: scale(1.05) translateY(-3px);
  box-shadow: 0 10px 20px rgba(22, 163, 74, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.3);
  filter: brightness(1.1);
}

.info a:active {
  transform: scale(0.98) translateY(0);
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.2);
  filter: brightness(0.9);
}

.info a:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.3), 0 6px 14px rgba(22, 163, 74, 0.4);
}

.info a .btn-icon {
  margin-right: 0.5rem;
  font-size: 1.2rem;
  vertical-align: middle;
  transition: transform 0.3s ease;
}

.info a:hover .btn-icon {
  transform: scale(1.2);
}

/* Table styling for guide */
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.5rem 0;
  background: #f1f5f9;
  border-radius: 12px;
  overflow: hidden;
}

th, td {
  border: 1px solid #e2e8f0;
  padding: 0.8rem;
  text-align: left;
  font-size: 1rem;
}

th {
  background-color: #e0e7ff;
  color: #1e40af;
  font-weight: 600;
}

td {
  color: #1e293b;
}

/* Responsive design */
@media (max-width: 768px) {
  .container {
    margin: 1.5rem;
    padding: 1.5rem;
  }

  h1 {
    font-size: 2rem;
  }

  h2 {
    font-size: 1.5rem;
  }

  form {
    max-width: 100%;
  }

  input, .btn-primary, .btn-back, .info a {
    width: 100%;
    font-size: 1rem;
  }

  .geogebra-container {
    height: 350px;
  }

  .mathjax {
    font-size: 1rem;
  }

  .btn-primary, .btn-back, .info a {
    padding: 0.8rem 1.5rem;
  }

  table {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: 1.8rem;
  }

  h2 {
    font-size: 1.3rem;
  }

  .calc-section {
    padding: 1rem;
  }

  .result-container img {
    margin: 1rem 0;
  }

  .mathjax {
    font-size: 0.9rem;
  }

  .btn-primary, .btn-back, .info a {
    font-size: 0.9rem;
    padding: 0.7rem 1.2rem;
  }

  .btn-icon {
    font-size: 1rem;
  }

  th, td {
    padding: 0.5rem;
    font-size: 0.85rem;
  }
}
"""

# HTML templates
INDEX_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora de Fourier</title>
    <style>{{ css }}</style>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <div class="container">
        <h1>Calculadora de Fourier</h1>

        <section class="calc-section">
            <h2>Serie de Fourier</h2>
            <p class="form-desc">Ingresa la función f(x), el valor de L y el número de términos N.</p>
            <form action="/serie" method="POST">
                <div class="form-group">
                    <label for="fx">Función f(x):</label>
                    <input type="text" id="fx" name="fx" required placeholder="Ejemplo: x**2">
                </div>
                <div class="form-group">
                    <label for="L">Valor de L:</label>
                    <input type="text" id="L" name="L" required placeholder="Ejemplo: pi">
                </div>
                <div class="form-group">
                    <label for="N">Número de términos (N):</label>
                    <input type="number" id="N" name="N" required placeholder="Ejemplo: 5">
                </div>
                <div class="button-wrapper">
                    <button type="submit" class="btn-primary btn-ripple">
                        <span class="btn-icon">📊</span> Calcular Serie
                    </button>
                </div>
            </form>
        </section>

        <section class="calc-section">
            <h2>Transformada de Fourier</h2>
            <p class="form-desc">Ingresa la función f(x) para calcular su transformada.</p>
            <form action="/transformada" method="POST">
                <div class="form-group">
                    <label for="fx_transform">Función f(x):</label>
                    <input type="text" id="fx_transform" name="fx" required placeholder="Ejemplo: exp(-x**2)">
                </div>
                <div class="button-wrapper">
                    <button type="submit" class="btn-primary btn-ripple">
                        <span class="btn-icon">📈</span> Calcular Transformada
                    </button>
                </div>
            </form>
        </section>

        <div class="info">
            <a href="/guia" class="btn-primary guia btn-ripple">
                <span class="btn-icon">📘</span> Ver Guía de Ejercicios
            </a>
        </div>
    </div>
</body>
</html>
"""

RESULTADOS_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ tipo }}</title>
    <style>{{ css }}</style>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <div class="container">
        <h1>{{ tipo }}</h1>
        <div class="result-container">
            <h2>Resultado Analítico</h2>
            <div class="mathjax">
                \\( {{ resultado|safe }} \\)
            </div>
            {% if imagen %}
            <h2>Representación Gráfica</h2>
            <img src="data:image/png;base64,{{ imagen }}" alt="Gráfico">
            {% endif %}
            <h2>Vista previa en GeoGebra</h2>
            <div class="geogebra-container">
                <iframe src="https://www.geogebra.org/calculator?predef={{ original_func }};{{ geo_func }}" frameborder="0"></iframe>
            </div>
            {% if original_func %}
            <p>Función original: {{ original_func }}</p>
            {% endif %}
            <p>Función transformada: {{ geo_func }}</p>
            <div class="button-wrapper">
                <a href="/" class="btn-back btn-ripple">
                    <span class="btn-icon">🔙</span> Volver
                </a>
            </div>
        </div>
    </div>
</body>
</html>
"""

GUIA_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guía de Ejercicios de Fourier</title>
    <style>{{ css }}</style>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <div class="container">
        <h1>Guía de Ejercicios de Fourier</h1>
        <p>A continuación se muestran ejemplos con su notación matemática, cómo escribirlos en la calculadora, el intervalo correspondiente, y el valor exacto de L que debes ingresar.</p>

        <section>
            <h2>Series de Fourier</h2>
            <table>
                <tr>
                    <th>Expresión Matemática</th>
                    <th>En la Calculadora</th>
                    <th>Intervalo [-L, L]</th>
                    <th>Valor de L a ingresar</th>
                </tr>
                <tr>
                    <td>\\( f(x) = x \\)</td>
                    <td>x</td>
                    <td>[-π, π]</td>
                    <td>pi ó 3.14</td>
                </tr>
                <tr>
                    <td>\\( f(x) = |x| \\)</td>
                    <td>Abs(x)</td>
                    <td>[-π, π]</td>
                    <td>pi</td>
                </tr>
                <tr>
                    <td>\\( f(x) = x^2 \\)</td>
                    <td>x**2</td>
                    <td>[-2, 2]</td>
                    <td>2</td>
                </tr>
                <tr>
                    <td>\\( f(x) = \\sin(x) \\)</td>
                    <td>sin(x)</td>
                    <td>[-π, π]</td>
                    <td>pi</td>
                </tr>
                <tr>
                    <td>\\( f(x) = x(\\pi - x) \\)</td>
                    <td>x*(pi - x)</td>
                    <td>[-π, π]</td>
                    <td>pi</td>
                </tr>
            </table>
        </section>

        <section>
            <h2>Transformadas de Fourier</h2>
            <table>
                <tr>
                    <th>Expresión Matemática</th>
                    <th>En la Calculadora</th>
                    <th>Dominio</th>
                    <th>L no requerido</th>
                </tr>
                <tr>
                    <td>\\( f(x) = e^{-x^2} \\)</td>
                    <td>exp(-x**2)</td>
                    <td>ℝ</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>\\( f(x) = \\text{rect}(x) \\)</td>
                    <td>Piecewise((1, Abs(x) < 0.5), (0, True))</td>
                    <td>ℝ</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>\\( f(x) = \\text{sinc}(x) \\)</td>
                    <td>sinc(x)</td>
                    <td>ℝ</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>\\( f(x) = \\sin(2\\pi x) \\)</td>
                    <td>sin(2*pi*x)</td>
                    <td>ℝ</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>\\( f(x) = e^{-|x|} \\)</td>
                    <td>exp(-Abs(x))</td>
                    <td>ℝ</td>
                    <td>-</td>
                </tr>
            </table>
        </section>

        <div class="info">
            <a href="/exportar-pdf" class="btn-primary btn-ripple">
                <span class="btn-icon">📄</span> Descargar esta guía como PDF
            </a>
        </div>

        <div class="button-wrapper">
            <a href="/" class="btn-back btn-ripple">
                <span class="btn-icon">🔙</span> Volver
            </a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML, css=CSS)

@app.route('/serie', methods=['POST'])
def serie_fourier():
    try:
        fx = request.form['fx']
        L_expr = request.form['L'].strip()
        if '=' in L_expr:
            L_expr = L_expr.split('=')[-1].strip()
        L = float(sp.N(sp.sympify(L_expr)))
        N = int(float(request.form['N']))

        x = sp.Symbol('x')
        f = sp.sympify(fx)

        a0 = (1/L) * sp.integrate(f, (x, -L, L))
        an = lambda n: (1/L) * sp.integrate(f * sp.cos(n * sp.pi * x / L), (x, -L, L))
        bn = lambda n: (1/L) * sp.integrate(f * sp.sin(n * sp.pi * x / L), (x, -L, L))

        fourier_series = a0/2
        for n in range(1, N + 1):
            fourier_series += an(n) * sp.cos(n * sp.pi * x / L) + bn(n) * sp.sin(n * sp.pi * x / L)

        f_lambdified = sp.lambdify(x, f, 'numpy')
        fs_lambdified = sp.lambdify(x, fourier_series, 'numpy')

        x_vals = np.linspace(-L, L, 1000)
        f_vals = f_lambdified(x_vals)
        fs_vals = fs_lambdified(x_vals)

        fig, ax = plt.subplots()
        ax.plot(x_vals, f_vals, label='f(x)')
        ax.plot(x_vals, fs_vals, label='Serie de Fourier', linestyle='--')
        ax.set_title('Serie de Fourier')
        ax.legend()
        ax.grid(True)

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        img_base64 = base64.b64encode(img.read()).decode('utf8')
        plt.close()

        # Simplify the Fourier series for GeoGebra by using numerical evaluation
        simplified_series = []
        for i in range(len(x_vals)):
            term = f"{fs_vals[i]:.2f}"
            simplified_series.append(term)
        # Instead of passing the complex series, pass a simplified version or the original function
        geo_func_str = str(f)  # Use the original function as a fallback for GeoGebra
        geo_func_str = geo_func_str.replace('**', '^').replace(' ', '').replace('pi', 'pi').replace('sin', 'sin').replace('cos', 'cos')
        geo_func_str_encoded = urllib.parse.quote(geo_func_str)

        original_func_str = str(f).replace('**', '^').replace(' ', '').replace('pi', 'pi').replace('sin', 'sin').replace('cos', 'cos').replace('exp', 'e^')
        original_func_encoded = urllib.parse.quote(original_func_str)

        return render_template_string(RESULTADOS_HTML,
                                     css=CSS,
                                     tipo='Serie de Fourier',
                                     resultado=sp.latex(fourier_series),
                                     imagen=img_base64,
                                     geo_func=geo_func_str_encoded,
                                     original_func=original_func_encoded)

    except Exception as e:
        return f"Ocurrió un error: {e}"

@app.route('/transformada', methods=['POST'])
def transformada_fourier():
    try:
        fx = request.form['fx'].strip()
        if '=' in fx:
            fx = fx.split('=')[-1].strip()

        x = sp.Symbol('x')
        w = sp.Symbol('w')

        f = sp.sympify(fx)
        F = sp.fourier_transform(f, x, w)

        F_abs = sp.Abs(F)
        F_lambda = sp.lambdify(w, F_abs, 'numpy')

        w_vals = np.linspace(-20, 20, 1000)
        F_vals = F_lambda(w_vals)

        fig, ax = plt.subplots()
        ax.plot(w_vals, F_vals, label='|F(w)|')
        ax.set_title('Transformada de Fourier: Magnitud')
        ax.set_xlabel('Frecuencia (w)')
        ax.set_ylabel('|F(w)|')
        ax.grid(True)
        ax.legend()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        img_base64 = base64.b64encode(img.read()).decode('utf8')
        plt.close()

        # Simplify the transform for GeoGebra
        geo_func = sp.simplify(F_abs)
        geo_func_str = str(geo_func)
        geo_func_str = geo_func_str.replace('**', '^').replace(' ', '').replace('pi', 'pi').replace('Abs', 'abs').replace('exp', 'e^')
        geo_func_str_encoded = urllib.parse.quote(geo_func_str)

        original_func_str = str(f).replace('**', '^').replace(' ', '').replace('pi', 'pi').replace('sin', 'sin').replace('cos', 'cos').replace('exp', 'e^')
        original_func_encoded = urllib.parse.quote(original_func_str)

        return render_template_string(RESULTADOS_HTML,
                                     css=CSS,
                                     tipo='Transformada de Fourier',
                                     resultado=sp.latex(F),
                                     imagen=img_base64,
                                     geo_func=geo_func_str_encoded,
                                     original_func=original_func_encoded)

    except Exception as e:
        return f"Ocurrió un error: {e}"

@app.route('/guia')
def guia():
    return render_template_string(GUIA_HTML, css=CSS)

@app.route('/exportar-pdf')
def exportar_pdf():
    html = render_template_string(GUIA_HTML, css=CSS)
    pdf_stream = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=pdf_stream)
    pdf_stream.seek(0)
    return send_file(pdf_stream, download_name="Guia_Fourier.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
