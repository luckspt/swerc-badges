import glob
import os
import pypdf

front_dir = './assembler/fronts'
#directory with front pngs (one for each person)
#we assume files are named '<role>*.png' 
#role should be in PascalCase (should alse be only a word, so just first letter capitalized)

back_dir = './assembler/backs'
#directory with back pdfs (one for each role)
#we assume files are named '<role>.png'
#role should be in PascalCase (should alse be only a word, so just first letter capitalized)

#IMPORTANT: having the original files in png instead of pdf really simplifies things.
#Vector graphics are not made to handle many shapes

output_dir = './assembler/output'
#where to put the final pdf files

roles = ['Volunteer','Contestant', 'Coach', 'Judge', 'Organizer', 'Sponsor']

positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right']

os.system(f"mkdir '{front_dir}/scaled'")
os.system(f"mkdir '{back_dir}/scaled'")

scale = 0.86
x_offset = '7.5mm'
y_offset = '15mm'

#this is unoptimal, there is probably a more elegant way of anchoring it to the corners
offset = {
    'top-left':     f"'-{x_offset} +{y_offset}'",
    'top-right':    f"'+{x_offset} +{y_offset}'",
    'bottom-left':  f"'-{x_offset} -{y_offset}'",
    'bottom-right': f"'+{x_offset} -{y_offset}'",
}

big_merge_call = f"pdfjam --a4paper --outfile '{output_dir}/all-roles-badges.pdf' -- "
for role in roles:
    #scaling backs
    for i, pos in enumerate(positions):
        os.system(f"pdfjam --scale {scale} --outfile \
                    '{back_dir}/scaled/{role}-{pos}.pdf' --a6paper --offset {offset[pos]} -- '{back_dir}/{role}.png'")

    merge_call = f"pdfjam --nup 2x2 --a4paper --outfile '{output_dir}/{role}-badges.pdf' -- "
    #scaling fronts
    for i, front_file in enumerate(glob.glob(f'{front_dir}/{role}*.png')):
        os.system(f"pdfjam --scale {scale} --outfile \
                  '{front_dir}/scaled/{role} {i}.pdf' --a6paper --offset {list(offset.values())[i % 4]} -- '{front_file}'")
        
        merge_call += f"'{front_dir}/scaled/{role} {i}.pdf' "
        if i % 4 == 3:
            for pos in positions:
                merge_call += f"'{back_dir}/scaled/{role}-{pos}.pdf' "
    
    if i % 4 != 3:
        for _ in range(3 - (i % 4)):
             merge_call += "'assembler/a6-blank-page.pdf' " 
             #I swear I'm not crazy. Else the last page with the fronts wouldn't be complete 

        for pos in positions:
                merge_call += f"'{back_dir}/scaled/{role}-{pos}.pdf' "

        
    #merging everything
    os.system(merge_call)


    stamp = pypdf.PdfReader("assembler/cut-guides.pdf").pages[0]
    writer = pypdf.PdfWriter(clone_from=f'{output_dir}/{role}-badges.pdf')
    for page in writer.pages:
        page.merge_page(stamp, over=True)


    writer.write(f'{output_dir}/{role}-badges.pdf')
    big_merge_call += f"'{output_dir}/{role}-badges.pdf' "

os.system(big_merge_call)
