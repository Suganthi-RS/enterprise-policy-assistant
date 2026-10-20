import axios from "axios";


const API_BASE_URL =
  "http://127.0.0.1:8000";


const api = axios.create({
  baseURL: API_BASE_URL,
});


export const loginUser = async (
  email,
  password
) => {

  const response = await api.post(
    "/auth/login",
    {
      email,
      password,
    },
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  return response.data;
};


export const getCurrentUser = async (
  token
) => {

  const response = await api.get(
    "/auth/me",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};


export const askPolicyQuestion = async (
  question,
  token
) => {

  const response = await api.post(
    "/qa/ask",
    null,
    {
      params: {
        question,
      },
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};


export const uploadDocument = async (
  file,
  documentType,
  token
) => {

  const formData = new FormData();

  formData.append(
    "file",
    file
  );

  formData.append(
    "document_type",
    documentType
  );


  const response = await api.post(
    "/documents/upload",
    formData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};


export const getDocuments = async (
  token
) => {

  const response = await api.get(
    "/documents/",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};


export const deleteDocument = async (
  documentId,
  token
) => {

  const response = await api.delete(
    `/documents/${documentId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};


export default api;