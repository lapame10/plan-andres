#!/usr/bin/env python3
"""En el plan de Andres sale escrito el HTML de un icono.

Pam, con captura: en la tarjeta de la racha aparece esto:

    🔥" style="height:21px;vertical-align:-4px;margin-right:1px">
    🔥 2 dias seguidos
    Te faltan 1 para 🔥

QUE PASA

Los iconos de la coleccion estan guardados como HTML:

    const ITEMS=[[1,'<img src="'+FIRE+'" style="height:22px">',LBL.chispa],[3,'⚡',...]]

Y la frase de "te faltan N para X" se pinta asi:

    rs.textContent = LBL.faltan.replace('{n}',sig[0]-n).replace('{ico}',sig[1]);

El problema es 'textContent'. textContent NO interpreta HTML: lo escribe tal
cual. Asi que en vez del dibujito sale la etiqueta entera escrita.

Es un fallo facil de cometer y dificil de ver, porque el codigo no da ningun
error: simplemente el icono se convierte en un monton de texto.

EL ARREGLO

Donde va un icono hay que usar innerHTML, no textContent. Y el resto de la frase
se deja igual, porque sale de LBL, que son textos de la app, no de nadie de
fuera. El unico numero que se mete (cuantos faltan) se pasa a texto con String
para que no pueda colarse nada.

Se arregla en los tres planes (andres, julien, karina) porque comparten el mismo
codigo y el fallo estaba en los tres.
"""
import os

BASE = '/Users/lapame10/.hermes/workspace/'
PLANES = ['plan-andres', 'plan-julien', 'plan-karina']

VIEJO = """    rs.textContent=sig?(LBL.faltan.replace('{n}',sig[0]-n).replace('{ico}',sig[1])):LBL.todos;"""

NUEVO = """    /* El icono de ITEMS es HTML (el del primer nivel es una imagen), asi que no
       puede ir en un textContent: se veria la etiqueta escrita en vez del
       dibujo. Pam lo vio justo asi en el movil. Aqui va con innerHTML; el resto
       de la frase sale de LBL, que son textos de la app, y el numero se pasa a
       texto con String. */
    if(sig){
      rs.innerHTML=LBL.faltan.replace('{n}',String(sig[0]-n)).replace('{ico}',sig[1]);
    } else {
      rs.textContent=LBL.todos;
    }"""

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
    elif 'if(sig){' in s and 'rs.innerHTML=LBL.faltan' in s:
        print('  · %s: ya estaba' % plan)
    else:
        print('  ✗ %s: NO COINCIDIO' % plan)

# y comprobar que no quede ningun otro textContent con HTML dentro
print()
print('  === otros sitios con el mismo peligro (textContent + algo que lleva <) ===')
import re
for plan in PLANES:
    ruta = os.path.join(BASE, plan, 'index.html')
    if not os.path.exists(ruta): continue
    s = open(ruta, encoding='utf-8').read()
    for m in re.finditer(r'\.textContent\s*=\s*([^;]{0,120});', s):
        cuerpo = m.group(1)
        if 'ITEMS' in cuerpo or 'sig[' in cuerpo or '<' in cuerpo or 'FIRE' in cuerpo:
            linea = s[:m.start()].count('\n') + 1
            print('   %s linea %d: %s' % (plan, linea, ' '.join(cuerpo.split())[:90]))
    print('   (%s revisado)' % plan)
