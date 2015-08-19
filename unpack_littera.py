#!/usr/bin/python

import xml.etree.ElementTree as et
import sys
import Image as img

def xint( s ): 
    return int( s ) if s.isdigit() else s

def kernings_list_to_dict( kernings_list ): 
    return dict((e['first'], dict((elm['second'],elm['amount']) for elm in kernings_list if e['first'] == elm['first'])) for e in kernings_list)

def process_littera( dom ): return {
    'chars': dict( [(unichr( int ( char.attrib['id'] )), ( dict([( k, xint(v), ) for k, v in char.attrib.items()]))) for char in dom.iter('char') if char.attrib['width'] > 0] ),
    'kernings': dom.find('kernings') != None and kernings_list_to_dict( [dict((k,int(v)) for k, v in kerning.attrib.items()) for kerning in dom.iter('kerning')] ),
    'pages': [dict((k,xint(v)) for k, v in page.attrib.items()) for page in dom.iter('page')],
    'common': dict((k,xint(v), ) for k, v in dom.find('common').attrib.items()),
    'info': dict((k,xint(v)) for k, v in dom.find('info').attrib.items()),
    'charscount': xint( dom.find('chars').attrib['count']),
    'kerningscount': dom.find('kernings') != None and xint( dom.find('kernings').attrib['count'] ),
}

def default_get_path_codes( littera, char, charinfo ):
    return '%s_%d.png' % (littera['info']['face'], charinfo['id'])

special_symbols = {
    '.': 'dot',
    ',': 'comma',
    '\\': 'backslash',
    '/': 'slash',
    '&': 'ampersand',
}

def default_get_path_symbols( littera, char, charinfo ):
    return '%s_%s.png' % (littera['info']['face'], special_symbols.get( char, char ))

def get_max_char_height( littera ):
    return max(char['height']+char['yoffset'] for char in littera['chars'].values())

def unpack_littera_page( littera, page, get_path=default_get_path_codes, common_divisor=(1,1) ):
    im = img.open( littera['pages'][page]['file'] )
    h = get_max_char_height( littera )
    while h % common_divisor[1] != 0: h = h + 1
    for k,v in dict((k,v) for k, v in littera['chars'].items() if v['page'] == page and v['width'] > 0 and v['height'] > 0).items():
        icrop = im.crop((v['x'],v['y'],v['x']+v['width'],v['y']+v['height']))
        w = v['width']
        while w % common_divisor[0] != 0: w = w + 1
        ires = img.new( 'RGBA', (w,h))
        ires.paste( icrop, (0,v['yoffset']))
        ires.save( get_path(littera,k,v))

def unpack_littera_font( xmlfont, symbolic, common_divisor ):
    littera = process_littera( et.parse( xmlfont ))
    print( get_max_char_height( littera ))
    unpack_littera_page( littera, 0, symbolic and default_get_path_symbols or default_get_path_codes, common_divisor )

if __name__=='__main__':
    if len( sys.argv ) <= 1:
        print('Usage: ./unpack_littera.py <font-file>.fnt [-s] [-w2] [-h2]')
        print('Unpack littera-created bitmap fonts into separate images')
        print('See http://kvazars.com/littera/')
        print('Save font in XML(.fnt) format')
        print('Output file format is <font-face>_<char-code>.png')
        print('Flags:')
        print('-s   output file format is <font-face>_<char>.png')
        print('-w2  make width dividable by 2' )
        print('-h2  make height dividable by 2' )
        print('-2   make width and height dividable by 2' )
    else:
        unpack_littera_font( sys.argv[1], '-s' in sys.argv, (('-w2' in sys.argv or '-2' in sys.argv) and 2 or 1, ('-h2' in sys.argv or '-2' in sys.argv) and 2 or 1) )
