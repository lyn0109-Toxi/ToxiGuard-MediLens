"""Keep narrative inactive-ingredient evidence distinct from structured identity."""
import re
import xml.etree.ElementTree as ET
NS={'h':'urn:hl7-org:v3'}

def narrative_sections(root):
    result=[]
    for section in root.findall('.//h:section',NS):
        code=section.find('h:code',NS)
        title=' '.join(''.join(section.find('h:title',NS).itertext()).split()) if section.find('h:title',NS) is not None else ''
        if not ((code is not None and code.get('code')=='51727-6') or title.casefold().strip()=='inactive ingredients'):
            continue
        text=section.find('h:text',NS)
        if text is None:continue
        # Keep footnotes at their original point of attachment, visibly bracketed.
        def walk(node):
            out=node.text or ''
            for child in node:
                value=walk(child)
                out+=(' ['+value+']') if child.tag.rsplit('}',1)[-1]=='footnote' else ' '+value
                out+=child.tail or ''
            return out
        result.append({'title':title or 'Inactive ingredients','text':' '.join(walk(text).split()),'original_xml':ET.tostring(text,encoding='unicode')})
    return result

def split_entries(text):
    # Editorial segmentation, not chemical identification. The complete paragraph is always retained.
    result=[];start=0;depth=0
    for j,c in enumerate(text):
        if c in '([':depth+=1
        elif c in ')]':depth=max(0,depth-1)
        elif c in ',;' and depth==0:
            result.append(text[start:j].strip());start=j+1
    result.append(text[start:].strip())
    return [x.rstrip('.') for x in result if x.strip()]

def inactive_evidence(product,sections):
    """Exact-name attachment only; unmatched narrative phrases never become asserted chemical identities."""
    rows=[]
    for j,i in enumerate(product['ingredients']):
        if not i['active']:
            rows.append({**i,'id':f'structured-{j}','origin':'structured','presence':'listed','narrative':[]})
    extras=[]
    for section in sections:
        for k,text in enumerate(split_entries(section['text'])):
            # A parenthetical qualifier can attach to an exact base name; it is preserved verbatim.
            base=re.sub(r'\s*[\[(].*','',text).strip().casefold()
            matched=[r for r in rows if r['name'].strip().casefold()==base]
            conditional=bool(re.search(r'\b(may|might)\s+(also\s+)?contain\b|\boptional\b|\bif present\b',text,re.I))
            if len(matched)==1:
                matched[0]['narrative'].append(text)
                if conditional:matched[0]['presence']='conditional'
            else:
                extras.append({'id':f'narrative-{len(extras)}','name':text,'active':False,'unii':None,'basis':None,'quantity':{'numerator':{'value':'','unit':''},'denominator':{'value':'','unit':''}},'origin':'narrative-only','presence':'conditional' if conditional else 'unmatched-narrative','narrative':[text],'original_xml':''})
    return rows+extras
