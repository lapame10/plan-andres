#!/usr/bin/env python3
"""LA CAUSA DE VERDAD del icono que salia escrito.

En el plan de Andres salia esto en la tarjeta de la racha:

    🔥" style="height:21px;vertical-align:-4px;margin-right:1px">
    🔥 2 dias seguidos
    Te faltan 1 para 🔥

Primero arregle la linea de "te faltan N para X", que tambien estaba mal (pintaba
HTML con textContent). Pero el resto de la etiqueta seguia saliendo, y venia de
aqui:

    fu.innerHTML='<img src="'+FIRE+'" style="...">'.repeat(Math.min(n,5))+(...)

EL BUG ES DE PRECEDENCIA

En JavaScript, el punto (la llamada a .repeat) se evalua ANTES que la suma. Asi
que esa linea NO hace "repite el <img> entero N veces". Hace esto:

    '<img src="'  +  FIRE  +  ('" style="...">'.repeat(N))

O sea: el <img> se escribe UNA vez, y lo que se repite es el trozo final. Con N=2
sale:

    <img src="URL" style="...">   +   " style="...">" style="...">

El primero es una imagen de verdad; el segundo es texto suelto, y es lo que Pam
veia escrito en la pantalla.

Medido: la expresion da 180 caracteres, no 242 (121 x 2). Los 121 son el <img>
completo y los 59 que sobran son el trozo repetido.

EL ARREGLO

Poner parentesis, para que se repita el <img> entero:

    ('<img src="'+FIRE+'" style="...">').repeat(Math.min(n,5))

Es un fallo facil de cometer y dificil de ver, porque no da ningun error: el
codigo corre, y simplemente en vez de dos dibujitos sale uno y un monton de
texto.
"""
import os

BASE = '/Users/lapame10/.hermes/workspace/'
PLANES = ['plan-andres', 'plan-julien', 'plan-karina']

VIEJO = """fu.innerHTML='<img src="'+FIRE+'" style="height:21px;vertical-align:-4px;margin-right:1px">'.repeat(Math.min(n,5))"""
NUEVO = """/* OJO CON LOS PARENTESIS: el punto se evalua antes que la suma, asi que
       sin ellos el .repeat() se aplicaba SOLO al trozo final de la cadena, no al
       <img> entero. Salia una imagen y el resto como texto suelto. */
    fu.innerHTML=('<img src="'+FIRE+'" style="height:21px;vertical-align:-4px;margin-right:1px">').repeat(Math.min(n,5))"""

print('  === los tres planes ===')
for plan in PLANES:
    ruta = os.path.join(BASE, plan, 'index.html')
    if not os.path.exists(ruta):
        print('  - %s: no existe' % plan); continue
    s = open(ruta, encoding='utf-8').read()
    if VIEJO in s:
        s = s.replace(VIEJO, NUEVO, 1)
        open(ruta, 'w', encoding='utf-8').write(s)
        print('  ✓ %s: arreglado' % plan)
    elif "').repeat(Math.min(n,5))" in s:
        print('  · %s: ya estaba' % plan)
    else:
        print('  ✗ %s: NO COINCIDIO' % plan)

# y comprobar que no queden mas .repeat() sin parentesis
print()
print('  === otros .repeat() pegados a una concatenacion ===')
import re, glob
peligrosos = 0
for plan in PLANES:
    ruta = os.path.join(BASE, plan, 'index.html')
    if not os.path.exists(ruta): continue
    s = open(ruta, encoding='utf-8').read()
    for m in re.finditer(r"[^\n(]{0,60}'[^']*'\.repeat\(|'[^']*'\.repeat\([^)]*\)", s):
        trozo = m.group(0)
        # si antes hay una suma, es peligroso
        antes = s[max(0, m.start()-80):m.start()]
        if '+' in antes and "'" in antes:
            linea = s[:m.start()].count('\n') + 1
            print('   ⚠ %s linea %d: %s' % (plan, linea, ' '.join(trozo.split())[:80]))
            peligrosos += 1
print('   %s' % ('✓ ninguno mas' if not peligrosos else '%d que revisar' % peligrosos))
