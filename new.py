import fitz
import spacy
import random
import string
from multiprocessing import Pool

# Function to extract text from a PDF using PyMuPDF
def extract_text_from_pdf(file_path):
    text = ''
    pdf_document = fitz.open(file_path)
    for page in pdf_document:
        text += page.get_text()
    pdf_document.close()
    return text

# Function to get paragraphs or sections from the extracted text
def get_paragraphs(text):
    # Split text into paragraphs or sections based on delimiter or markers specific to the document
    # Return a list of paragraphs or sections
    # For demonstration purposes, splitting by newline characters
    return text.split('\n')

# Process text chunk using Spacy
def process_text_chunk(chunk):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(chunk)

    mcq_list = []
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.split()) > 10]

    for sentence in sentences:
        tokens = nlp(sentence)
        important_words = [token.text for token in tokens if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'ADV'] and token.dep_ in ['nsubj', 'dobj', 'amod', 'advmod']]

        if not important_words:
            continue

        selected_word = random.choice(important_words)
        dashed_sentence = sentence.replace(selected_word, "-" * len(selected_word))

        options = [selected_word]

        while len(options) < 4:
            random_option = random.choice(important_words)
            if random_option not in options:
                options.append(random_option)

        random.shuffle(options)

        mcq = {
            "question": f"{dashed_sentence}",
            "options": options,
            "correct_answer": options.index(selected_word) + 1,
            "answer_text": selected_word
        }
        mcq_list.append(mcq)

    return mcq_list

# Save generated MCQs to a file
def save_to_file(questions, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for idx, mcq in enumerate(questions, start=1):
            file.write(f"Question {idx}:\n")
            file.write(f"{mcq['question']}\n\n")

            for i, option in enumerate(mcq['options'], start=1):
                file.write(f"{string.ascii_uppercase[i-1]}. {option}\n")

            file.write(f"Correct Answer: {string.ascii_uppercase[mcq['correct_answer'] - 1]}\n")
            file.write("************************************\n\n")

def main():
    file_path = '/home/rk/Desktop/pdf extractor/Chapter_1.pdf'  # Replace with the path to your PDF file
    num_questions = int(input("Enter the number of questions to generate: "))
    output_file_path = '/home/rk/Desktop/pdf extractor/generated_questions.txt'  # Replace with the desired output file path

    extracted_text = extract_text_from_pdf(file_path)
    paragraphs = get_paragraphs(extracted_text)

    all_mcqs = []
    with Pool() as pool:
        mcq_chunks = pool.map(process_text_chunk, paragraphs)
        for mcqs in mcq_chunks:
            all_mcqs.extend(mcqs)

    save_to_file(all_mcqs[:num_questions], output_file_path)
    print(f"Questions and answers generated successfully and saved to {output_file_path}")

if __name__ == "__main__":
    main()

