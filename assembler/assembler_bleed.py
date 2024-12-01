import glob
import os

front_dir = '/Users/simaoleal/Desktop/SWERC 24/front'
#directory with front pdfs (one for each person)
#we assume files are named '<role> <some number>.pdf' 
#role should be lower case

back_dir = '/Users/simaoleal/Desktop/SWERC 24/back'
#directory with back pdfs (one for each role)
#we assume files are named '<role>.pdf'
#role should be lower case

output_dir = '/Users/simaoleal/Desktop/SWERC 24/output'
#where to put the final pdf files

roles = ['Volunteer'] #['Contestant', 'Coach', 'Jury', 'Organizer', 'Volunteer', 'Sponsor']

positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right']

os.system(f"mkdir '{front_dir}/scaled'")
os.system(f"mkdir '{back_dir}/scaled'")

scale = 0.93

for role in roles:
    #scaling backs
    for i, pos in enumerate(positions):
        os.system(f"pdfjam --scale {scale} --outfile \
                    '{back_dir}/scaled/{role}-{pos}.pdf' --a6paper -- '{back_dir}/{role}.pdf'")

    merge_call = f"pdfjam --nup 2x2 --a4paper --outfile '{output_dir}/{role}-badges-bleed.pdf' -- "
    #scaling fronts
    for i, front_file in enumerate(glob.glob(f'{front_dir}/{role}*.pdf')):
        os.system(f"pdfjam --scale {scale} --outfile \
                  '{front_dir}/scaled/{role} {i}.pdf' --a6paper -- '{front_file}'")
        
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


