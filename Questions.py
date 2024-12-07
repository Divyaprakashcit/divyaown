import csv
import pandas as pd
from groq import Groq

# Initialize Groq client
client = Groq(
    api_key="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"
)

# Function to generate harder options using Groq
def generate_harder_options(question_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates challenging but relevant answer options for quiz questions."},
        {"role": "user", "content": f"Generate 4 harder and relevant answer options for the following question:\n{question_text}"}
    ]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=messages,
            temperature=0.8,
            max_tokens=256,
            top_p=1,
            stream=False
        )

        # Debugging: Check the structure of the response
        print(f"Completion response: {completion}")

        # Extract response text
        if hasattr(completion, 'choices') and hasattr(completion.choices[0], 'message'):
            response = completion.choices[0].message.content
        else:
            raise ValueError("Unexpected response structure from Groq.")

        # Parse the response into clean options
        options = response.split("\n")
        options = [opt.strip() for opt in options if opt.strip()]  # Ensure clean formatting
        options = [opt for opt in options if not opt.lower().startswith("here are")]

        if len(options) < 4:
            raise ValueError("Fewer than 4 options generated.")

        return options[:4]  # Return only the first four options

    except Exception as e:
        print(f"Error generating options: {e}")
        return []


# Process all quiz questions and generate answer options
def process_quiz_file(input_csv, output_excel):
    # Read CSV file
    data = pd.read_csv(input_csv)

    # Prepare list to store generated options
    options_data = []
    option_id_counter = 1  # Initialize counter for auto-incremented option IDs

    for index, row in data.iterrows():
        question_id = row['question_type_id']
        question_text = row['question_text']

        # Debugging: Log current question being processed
        print(f"Processing question_id: {question_id}, question_text: '{question_text}'")

        # Generate answer options using Groq
        try:
            generated_options = generate_harder_options(question_text)

            # Debugging: Log generated options
            print(f"Generated options for question_id {question_id}: {generated_options}")

            if len(generated_options) != 4:
                print(f"Warning: Did not generate 4 options for question_id {question_id}. Skipping.")
                continue

            # Add generated options to the list
            for option in generated_options:
                options_data.append({
                    "option_id": option_id_counter,  # Assign auto-incremented ID
                    "question_id": question_id,
                    "option_text": option,
                    "is_correct": 1 if option == generated_options[0] else 0  # Mark the first option as correct
                })
                option_id_counter += 1  # Increment the counter

        except Exception as e:
            print(f"Error generating options for question_id {question_id}: {e}")

    # Write options to Excel file
    if options_data:
        df = pd.DataFrame(options_data)
        df.to_excel(output_excel, index=False)
        print(f"Generated options saved to {output_excel}")
    else:
        print("No options were generated. Please check the input or the Groq service.")


# Input and output file paths
input_csv = "quiz_questions.csv"  # Replace with the path to your input CSV file
output_excel = "generated_options.xlsx"  # Replace with the path to your output Excel file

# Execute the function
process_quiz_file(input_csv, output_excel)
