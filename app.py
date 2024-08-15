# app.py
from flask import Flask, request, session, redirect, url_for, render_template, flash, make_response, jsonify
from functools import wraps
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
import os
import tempfile

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'


def nocache(view):

    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers[
            'Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return no_cache


# Database configuration
user = os.environ['USER']
host = os.environ['HOST']
password = os.environ['PASSWORD']
database = os.environ['DATABASE']
port = os.environ['PORT']

connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


@app.route('/', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        engine = create_engine(connection_string)
        with engine.connect() as connection:
            result = connection.execute(
                text('SELECT * FROM students WHERE email = :email'),
                {'email': email})
            account = result.mappings().fetchone()
            #print(account)

        if account and check_password_hash(account['password_hash'], password):
            session['loggedin'] = True

            global student
            student = account['id']

            session['id'] = account['id']
            session['username'] = account['first_name']
            return redirect(url_for('student_home'))
        else:
            flash('Incorrect email/password')

    return render_template('studentLogin.html')


@app.route('/studentSignUp', methods=['GET', 'POST'])
def student_signUp():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        school_name = request.form['school_name']
        school_email = request.form['school_email']
        password = request.form['password']

        _hashed_password = generate_password_hash(password)

        engine = create_engine(connection_string)
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM students WHERE email = :email"),
                {'email': school_email})
            account = result.fetchone()

            if account:
                flash('Account already exists!')
            else:
                insert_statement = text(
                    "INSERT INTO students (first_name, last_name, school, password_hash, email) "
                    "VALUES (:first_name, :last_name, :school, :password_hash, :email)"
                ).bindparams(first_name=first_name,
                             last_name=last_name,
                             school=school_name,
                             password_hash=_hashed_password,
                             email=school_email)

                engine = create_engine(connection_string)
                with engine.connect() as connection:
                    connection.execute(insert_statement)
                    connection.commit()
                    return render_template('studentLogin.html')

    return render_template('studentSignUp.html')


@app.route('/adminLogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('career_center_email')
        password = request.form.get('password')

        engine = create_engine(connection_string)
        with engine.connect() as connection:
            result = connection.execute(
                text('SELECT * FROM admins WHERE email = :email'),
                {'email': email})
            account = result.mappings().fetchone()

        if account and check_password_hash(account['password_hash'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['school'] = account['school']

            global admin_school
            admin_school = account['school']

            return redirect(url_for('admin_home'))
        else:
            flash('Incorrect email/password')

    return render_template('adminLogin.html')


@app.route('/adminSignUp', methods=['GET', 'POST'])
def admin_signUp():
    if request.method == 'POST':
        school = request.form.get('school_name')
        career_center_email = request.form.get('career_center_email')
        password = request.form.get('password', '')

        _hashed_password = generate_password_hash(password)

        engine = create_engine(connection_string)
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM admins WHERE email = :email"),
                {'email': career_center_email})
            account = result.fetchone()

            if account:
                render_template('adminSignUp.html')
            else:
                engine = create_engine(connection_string)
                with engine.connect() as connection:
                    connection.execute(
                        text(
                            "INSERT INTO admins (school, email, password_hash) VALUES (:school, :email, :password_hash)"
                        ), {
                            'school': school,
                            'email': career_center_email,
                            'password_hash': _hashed_password
                        })
                    connection.commit()
                return redirect(url_for('admin_login'))

    return render_template('adminSignUp.html')


@app.route('/home')
@nocache
def student_home():
    return render_template('studentHome.html')


@app.route('/adminHome')
@nocache
def admin_home():

    query = text(
        "SELECT r.id, r.request_text, r.request_date, r.status, s.first_name, s.last_name, s.email "
        "FROM requests r "
        "JOIN students s ON r.student_id = s.id "
        "WHERE s.school = :school").bindparams(school=admin_school)

    engine = create_engine(connection_string)
    with engine.connect() as connection:
        requests = connection.execute(query)
        #print("MyRequests:", requests)

    return render_template('adminHome.html', requests=requests)


@app.route('/mentor', methods=['GET', 'POST'])
@nocache
def mentor():
    if request.method == 'GET':
        student_id = session.get('id')
        query = text("SELECT * FROM requests WHERE student_id = :student_id")
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            results = connection.execute(query, {
                'student_id': student_id
            }).fetchall()

        formatted_results = []
        for result in results:
            request_date = result[3]
            formatted_date = request_date.strftime("%m/%d/%Y")
            formatted_row = {
                'request_text': result[2],
                'request_date': formatted_date,
                'status': result[4]
            }
            formatted_results.append(formatted_row)

        return render_template('mentor.html', requests=formatted_results)

    if request.method == 'POST':
        try:
            request_text = request.form['student_request']
            student_id = session.get('id')  # Use session.get to avoid KeyError
            #print(f"Request Text: {request_text}, Student ID: {student_id}")

            request_query = text(
                "INSERT INTO requests (student_id, request_text) "
                "VALUES (:student_id, :request_text)").bindparams(
                    student_id=student_id, request_text=request_text)

            engine = create_engine(connection_string)
            # Execute the query
            with engine.connect() as connection:
                connection.execute(request_query)
                connection.commit()

            query = text(
                "SELECT * FROM requests WHERE student_id = :student_id")
            with engine.connect() as connection:
                result = connection.execute(query, {
                    'student_id': student_id
                }).fetchall()

            return render_template('mentor.html', requests=result), 200

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'Failed to save request.'}), 500


@app.route('/update_request_status', methods=['POST'])
def update_request_status():
    data = request.json
    request_id = data.get('request_id')
    new_status = data.get('new_status')

    if not request_id or not new_status:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            update_query = text(
                "UPDATE requests SET status = :new_status WHERE id = :request_id"
            )
            connection.execute(update_query, {
                'new_status': new_status,
                'request_id': request_id
            })
            connection.commit()

        # Fetch the updated status from the database to confirm the change
        with engine.connect() as connection:
            select_query = text(
                "SELECT status FROM requests WHERE id = :request_id")
            result = connection.execute(select_query, {
                'request_id': request_id
            }).fetchone()
            updated_status = result[0] if result else None

        return jsonify({'success': True, 'updated_status': updated_status})
    except Exception as e:
        print(f"Error updating request status: {str(e)}")
        return jsonify({'success': False, 'error': 'Database error'}), 500


# Initialize the language model
llm = ChatOpenAI(name="gpt-4o-mini", temperature=1.0)

# Create a memory object
memory = ConversationBufferMemory(memory_key="chat_history",
                                  return_messages=True)

embedding = OpenAIEmbeddings()

template = """
You are a Career Guide. Provide concise and actionable feedback on resumes and specific questions. When asked to rewrite or improve content, offer direct examples and suggestions. Avoid repeating greetings if the conversation is ongoing. Focus on transforming given content into more impactful statements using action verbs and quantifiable results. Do not provide unsolicited career path suggestions unless explicitly requested.

Conversation History:
{chat_history}

Resume Context:
{context}

Student Question: {question}

Response:
"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    # Load the PDF using the temporary file path
    loader = PyMuPDFLoader(temp_file_path)
    data = loader.load()

    # Add to ChromaDB
    vectordb = Chroma.from_documents(
        documents=data,
        embedding=embedding,
        persist_directory=None  # Do not persist the database
    )

    # Store the vector database in the session
    #session['vectordb'] = vectordb

    global qa_chain

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectordb.as_retriever(search_kwargs={'k': 1}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT})

    # Clean up the temporary file
    os.remove(temp_file_path)
    #flash('File uploaded and processed successfully!', 'success')
    #return redirect(request.url)
    return jsonify({'success': 'File uploaded and processed'}), 200


@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'GET':
        return render_template('resumeReview.html')
    user_question = request.json['question']
    result = qa_chain.invoke({"question": user_question})
    answer = result['answer']
    memory.chat_memory.add_user_message(user_question)
    memory.chat_memory.add_ai_message(answer)
    #print(memory)

    return jsonify({'answer': answer})


'''# Initialize components for admin chat
admin_llm = ChatOpenAI(name="gpt-4o-mini", temperature=0.7)
admin_memory = ConversationBufferMemory(return_messages=True)

admin_template = """
You are an AI assistant for a career center administrator. Your task is to analyze and summarize student mentorship requests.

Context of student requests:
{context}

Chat History:
{chat_history}

Administrator's Question: {question}

Please provide a concise and informative response based on the given context, chat history, and question.
"""

admin_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=admin_template
)

@app.route('/admin_chat', methods=['POST'])
def admin_chat():
    user_question = request.json['question']

    # Fetch all requests from the database
    engine = create_engine(connection_string)
    with engine.connect() as connection:
        query = text("SELECT r.request_text, r.request_date, r.status, s.first_name, s.last_name, s.school "
                     "FROM requests r "
                     "JOIN students s ON r.student_id = s.id "
                     "WHERE s.school = :school")
        results = connection.execute(query, {'school': session['school']}).fetchall()

    # Prepare the context for the AI
    context = "Student Requests:\n"
    for result in results:
        context += f"- {result.first_name} {result.last_name} from {result.school}: '{result.request_text}' (Status: {result.status}, Date: {result.request_date})\n"

    # Create or update the LLMChain
    admin_chain = LLMChain(
        llm=admin_llm,
        prompt=admin_prompt,
        memory=admin_memory,
        verbose=True
    )

    # Generate response
    response = admin_chain.predict(context=context, question=user_question)

    return jsonify({'answer': response})

'''


@app.route('/logout')
def logout():
    #session.pop('loggedin', None)
    #session.pop('id', None)
    #session.pop('username', None)
    session.clear()
    return redirect(url_for('student_login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
