import React from "react";
import ChatWidget from "../components/ChatWidget";
import { UserProvider } from "../components/UserContext";

export default function Root({ children }) {
  return (
    <UserProvider>
      {children}
      <ChatWidget />
    </UserProvider>
  );
}
