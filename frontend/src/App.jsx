import {
  useState,
  useEffect,
} from "react";

import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";

import {
  loginUser,
  getCurrentUser,
  askPolicyQuestion,
  uploadDocument,
  getDocuments,
  deleteDocument,
} from "./services/api";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);


  const handleLogin = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const tokenResponse = await loginUser(
        email,
        password
      );

      const token = tokenResponse.access_token;

      localStorage.setItem(
        "access_token",
        token
      );

      const user = await getCurrentUser(token);

      localStorage.setItem(
        "user",
        JSON.stringify(user)
      );

      if (user.role === "admin") {
        navigate("/admin");
      } else {
        navigate("/employee");
      }

    } catch (error) {
      console.error(error);

      setError(
        "Invalid email or password."
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="login-page">

      <div className="login-card">

        <h1>
          Enterprise{" "}
          <span className="app-title">
            Policy Assistant
          </span>
        </h1>

        <p className="login-subtitle">
          Sign in to access company policies
          and information.
        </p>


        <form onSubmit={handleLogin}>

          <div className="form-group">
            <label>Email</label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
            />
          </div>


          <div className="form-group">
            <label>Password</label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              required
            />
          </div>


          {error && (
            <p className="error-message">
              {error}
            </p>
          )}


          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading
              ? "Signing in..."
              : "Sign In"}
          </button>

        </form>

      </div>

    </div>
  );
}

function EmployeeDashboard() {

  const navigate = useNavigate();


  const user = JSON.parse(
    localStorage.getItem("user") || "{}"
  );

  const token = localStorage.getItem(
    "access_token"
  );


  const [question, setQuestion] = useState("");

  const [messages, setMessages] = useState([
    {
      type: "assistant",
      text:
        "Hello! I'm your Enterprise Policy Assistant. Ask me anything about your company's HR, leave, insurance, benefits, or other policies."
    }
  ]);


  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");


  const handleAsk = async (event) => {

    event.preventDefault();


    const trimmedQuestion =
      question.trim();


    if (!trimmedQuestion || loading) {
      return;
    }


    setError("");


    // Add user question immediately

    setMessages((previous) => [
      ...previous,
      {
        type: "user",
        text: trimmedQuestion
      }
    ]);


    setQuestion("");

    setLoading(true);


    try {

      const response =
        await askPolicyQuestion(
          trimmedQuestion,
          token
        );


      setMessages((previous) => [
        ...previous,
        {
          type: "assistant",
          text: response.answer,
          sources: response.sources || []
        }
      ]);


    } catch (error) {

      console.error(error);


      setError(
        "Unable to get an answer. Please try again."
      );


      setMessages((previous) => [
        ...previous,
        {
          type: "assistant",
          text:
            "Sorry, I couldn't process your question right now. Please try again."
        }
      ]);


    } finally {

      setLoading(false);

    }
  };


  const handleClearChat = () => {

    setMessages([
      {
        type: "assistant",
        text:
          "Hello! I'm your Enterprise Policy Assistant. Ask me anything about your company's HR, leave, insurance, benefits, or other policies."
      }
    ]);

    setError("");

  };


  const handleLogout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user"
    );

    navigate("/");

  };


  return (
    <div className="dashboard">


      {/* Header */}

      <header className="topbar">

        <div>

          <h2>
            Enterprise Policy Assistant
          </h2>

          <span>
            Employee Portal
          </span>

        </div>


        <div className="user-section">

          <span>
            {user.name || "Employee"}
          </span>


          <button
            className="clear-chat-button"
            onClick={handleClearChat}
          >
            New Chat
          </button>


          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>



      {/* Chat */}

      <main className="chat-main">


        <section className="chat-header">

          <div>

            <h1>
              Ask about company policies
            </h1>

            <p>
              Get answers from your company's
              official policy documents.
            </p>

          </div>

        </section>



        <section className="chat-container">


          <div className="messages">


            {messages.map(
              (message, index) => (

                <div
                  key={index}
                  className={`message-row ${message.type}`}
                >

                  <div className="message-avatar">

                    {message.type === "assistant"
                      ? "AI"
                      : "You"}

                  </div>


                  <div className="message-content">

                    <div className="message-bubble">

                      {message.text}

                    </div>



                    {/* Sources */}

                    {message.type === "assistant" &&
                      message.sources &&
                      message.sources.length > 0 && (

                        <div className="chat-sources">

                          <h4>
                            Sources
                          </h4>


                          <div className="source-list">

                            {message.sources.map(
                              (source, sourceIndex) => (

                                <div
                                  className="chat-source-card"
                                  key={
                                    source.chunk_id ||
                                    sourceIndex
                                  }
                                >

                                  <div className="chat-source-title">

                                    <span>
                                      📄
                                    </span>

                                    <strong>
                                      {source.document}
                                    </strong>

                                  </div>


                                  <div className="chat-source-meta">

                                    <span>
                                      Page{" "}
                                      {source.page_number}
                                    </span>

                                    <span>
                                      Chunk{" "}
                                      {source.chunk_index}
                                    </span>

                                  </div>


                                  <p>
                                    {source.content_preview}
                                  </p>

                                </div>

                              )
                            )}

                          </div>

                        </div>

                      )}

                  </div>

                </div>

              )
            )}



            {/* Loading */}

            {loading && (

              <div className="message-row assistant">

                <div className="message-avatar">
                  AI
                </div>


                <div className="message-content">

                  <div className="message-bubble loading-bubble">

                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>

                  </div>

                </div>

              </div>

            )}

          </div>



          {/* Error */}

          {error && (

            <div className="chat-error">
              {error}
            </div>

          )}



          {/* Input */}

          <form
            className="chat-input-area"
            onSubmit={handleAsk}
          >

            <input
              type="text"
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              placeholder="Ask a question about company policies..."
              disabled={loading}
            />


            <button
              type="submit"
              disabled={
                loading ||
                !question.trim()
              }
            >

              {loading
                ? "..."
                : "Ask"}

            </button>

          </form>


          <p className="chat-disclaimer">
            Answers are generated from available
            company policy documents.
          </p>


        </section>

      </main>

    </div>
  );
}


function AdminDashboard() {

  const navigate = useNavigate();

  const user = JSON.parse(
    localStorage.getItem("user") || "{}"
  );

  const token = localStorage.getItem(
    "access_token"
  );


  const [file, setFile] = useState(null);
  const [documentType, setDocumentType] = useState("hr");

  const [documents, setDocuments] = useState([]);

  const [loading, setLoading] = useState(false);
  const [loadingDocuments, setLoadingDocuments] = useState(true);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");


  const loadDocuments = async () => {

    try {

      setLoadingDocuments(true);

      const response =
        await getDocuments(token);

      setDocuments(
        response.documents || []
      );

    } catch (error) {

      console.error(error);

      setError(
        "Unable to load uploaded policies."
      );

    } finally {

      setLoadingDocuments(false);

    }
  };


  const handleUpload = async (event) => {

    event.preventDefault();

    if (!file) {

      setError(
        "Please select a PDF file."
      );

      return;
    }


    setLoading(true);
    setError("");
    setMessage("");


    try {

      await uploadDocument(
        file,
        documentType,
        token
      );

      setMessage(
        "Policy uploaded successfully."
      );

      setFile(null);

      event.target.reset();

      await loadDocuments();

    } catch (error) {

      console.error(error);

      const detail =
        error.response?.data?.detail;

      setError(
        detail ||
        "Unable to upload the policy."
      );

    } finally {

      setLoading(false);

    }
  };


  const handleDelete = async (
    documentId,
    filename
  ) => {

    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) {
      return;
    }


    setError("");
    setMessage("");


    try {

      await deleteDocument(
        documentId,
        token
      );

      setMessage(
        "Policy deleted successfully."
      );

      await loadDocuments();

    } catch (error) {

      console.error(error);

      const detail =
        error.response?.data?.detail;

      setError(
        detail ||
        "Unable to delete the policy."
      );
    }
  };


  const handleLogout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user"
    );

    navigate("/");

  };


  // Load policies when dashboard opens

 useEffect(() => {
  loadDocuments();
}, []);

  return (
    <div className="dashboard">

      <header className="topbar">

        <div>
          <h2>
            Enterprise Policy Assistant
          </h2>

          <span>
            Admin Portal
          </span>
        </div>


        <div className="user-section">

          <span>
            {user.name || "Admin"}
          </span>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>


      <main className="admin-main">

        <section className="admin-header">

          <h1>
            Policy Management
          </h1>

          <p>
            Upload and manage company policy
            documents used by the AI assistant.
          </p>

        </section>


        {message && (
          <div className="success-box">
            {message}
          </div>
        )}


        {error && (
          <div className="error-box">
            {error}
          </div>
        )}


        <section className="upload-card">

          <h2>
            Upload Policy
          </h2>

          <p>
            Upload a PDF document containing
            company policy information.
          </p>


          <form
            className="upload-form"
            onSubmit={handleUpload}
          >

            <div className="form-group">

              <label>
                Policy Type
              </label>

              <select
                value={documentType}
                onChange={(event) =>
                  setDocumentType(
                    event.target.value
                  )
                }
              >

                <option value="hr">
                  HR Policy
                </option>

                <option value="health_insurance">
                  Health Insurance
                </option>

                <option value="leave">
                  Leave Policy
                </option>

                <option value="benefits">
                  Benefits
                </option>

                <option value="general">
                  General Policy
                </option>

              </select>

            </div>


            <div className="form-group">

              <label>
                Policy PDF
              </label>

              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={(event) =>
                  setFile(
                    event.target.files[0]
                  )
                }
              />

              {file && (
                <p className="selected-file">
                  Selected: {file.name}
                </p>
              )}

            </div>


            <button
              type="submit"
              className="upload-button"
              disabled={loading}
            >
              {loading
                ? "Uploading..."
                : "Upload Policy"}
            </button>

          </form>

        </section>


        <section className="documents-section">

          <div className="documents-header">

            <div>
              <h2>
                Uploaded Policies
              </h2>

              <p>
                {documents.length} policy
                {documents.length !== 1
                  ? " documents"
                  : " document"}
              </p>
            </div>

          </div>


          {loadingDocuments ? (

            <div className="empty-state">
              Loading policies...
            </div>

          ) : documents.length === 0 ? (

            <div className="empty-state">

              <h3>
                No policies uploaded
              </h3>

              <p>
                Upload your first policy document
                using the form above.
              </p>

            </div>

          ) : (

            <div className="documents-table-wrapper">

              <table className="documents-table">

                <thead>

                  <tr>

                    <th>
                      Document
                    </th>

                    <th>
                      Type
                    </th>

                    <th>
                      Uploaded
                    </th>

                    <th>
                      Action
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {documents.map(
                    (document) => (

                      <tr
                        key={document.id}
                      >

                        <td>

                          <strong>
                            {document.filename}
                          </strong>

                        </td>


                        <td>

                          <span className="document-type">

                            {document.document_type
                              .replace(
                                "_",
                                " "
                              )}

                          </span>

                        </td>


                        <td>

                          {new Date(
                            document.uploaded_at
                          ).toLocaleDateString()}

                        </td>


                        <td>

                          <button
                            className="delete-button"
                            onClick={() =>
                              handleDelete(
                                document.id,
                                document.filename
                              )
                            }
                          >
                            Delete
                          </button>

                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </section>

      </main>

    </div>
  );
}


function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Login />}
        />

        <Route
          path="/admin"
          element={<AdminDashboard />}
        />

        <Route
          path="/employee"
          element={<EmployeeDashboard />}
        />

        <Route
          path="*"
          element={
            <Navigate to="/" />
          }
        />

      </Routes>

    </BrowserRouter>

  );
}


export default App;