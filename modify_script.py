import os
import re

current_dir = os.path.dirname(__file__)
chapters_dir = os.path.join(current_dir,'chapters')
source_dir = os.path.join(current_dir,'sphinx','source')
files_in_chapters = sorted([f for f in os.listdir(chapters_dir)])

def combine_to_readme():
    with open('README.md', 'w') as readme_file:
        for md_file in files_in_chapters:
            md_file_path = os.path.join(chapters_dir, md_file)
            with open(md_file_path, 'r') as chapter_file:
                content = chapter_file.read()
                readme_file.write(content)

def admonitation(text, match):

    # Define the regular expression pattern
    pattern = re.compile(r'> :(\w+): (.+)|> (.+)')
    # Replace and process matches
    new_text = ''
  
    for m in pattern.finditer(text):
        if m.group(1):  # Matched > :word: content
            new_text += f'```{{{m.group(1)}}} {m.group(2)}\n'
        elif m.group(3):  # Matched > (other)
            new_text += f'{m.group(3)}\n'

    new_text += '```'

    return new_text  
 
def header_reference(text, match):
    subtext = match.group(1)

    # Check if the end of the text contains a non-alpha character
    if not subtext[-1].isalpha():
        # remove this non-alpha character
        subtext = subtext.rstrip(subtext[-1]) 
        
    # Split the subtext into a list of words
    word_list = subtext.split()
    # Create a new text with '-' between words and wrap in brackets
    new_text = '(' + '-'.join(word_list) + ')=\n# ' + match.group(1)
    return new_text

def consecutive_header(text, match):
    return text[1:]

def math(text, match):
    pass

def pattern_dict():
    return {'> :' : admonitation,
            '^## (.+)' : header_reference,
            '##(#)+' : consecutive_header
            # some more patterns will be added
            }

def modify_paragraphs(text):
    
    modified_text = ''
    patterns = pattern_dict()

    # Split the text into paragraphs
    paragraphs = [paragraph.strip() for paragraph in text.split('\n\n') if paragraph.strip()]

    # Find paragraphs with the specific patterns and modify it.
    for paragraph in paragraphs:

        patterns = {re.compile(pattern) : art for pattern, art  in patterns.items()} 

        # the paragraph matchs no pattern in pattern_dict
        if(all(not pattern.match(paragraph) for pattern in patterns)):
            modified_text += paragraph + '\n\n'
        else:
            pattern_counter = 0
            for pattern, modify_art in patterns.items():
                match = re.match(pattern, paragraph)
                if match:
                    # at the first pattern matching add modified text to the original
                    if pattern_counter == 0:
                        modified_text += modify_art(paragraph, match)
                        pattern_counter += 1
                    # since the second pattern matching just modify the text
                    else:
                        modified_text = modify_art(modified_text, match)     
            modified_text += '\n\n'

    return modified_text 

def modify_md_files(read_file, write_file):
    with open(read_file, 'r') as read_file:
        content = read_file.read()
        modified_content = modify_paragraphs(content)
        with open(write_file, 'w') as write_file:
            write_file.write(modified_content)

if __name__ == "__main__":
    combine_to_readme()
    for file in files_in_chapters:
        read_file_path = os.path.join(chapters_dir, file)
        write_file_path = os.path.join(source_dir, file)
        modify_md_files(read_file_path, write_file_path)
        