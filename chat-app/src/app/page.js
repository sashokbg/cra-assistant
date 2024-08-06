'use client'

import {
  ChatContainer,
  MainContainer,
  Message,
  MessageInput,
  MessageList,
  MessageSeparator,
} from "@chatscope/chat-ui-kit-react";
import {useEffect, useState} from "react";
import {socket} from '@/socket';

export default function Page() {
  const [connected, setConnected] = useState(false)
  const [messages, setMessages] = useState([])

  useEffect(() => {
    function onConnect() {
      setConnected(true);
    }

    function onDisconnect() {
      setConnected(false);
    }

    function onSystemMessage(data) {
      console.log("system message received", data);
      messages.push({
        role: "system",
        content: data.data.content
      });
      setMessages(messages)
      // updateBoard("board", messages);
    }


    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('system-message', onSystemMessage);

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('system-message', onSystemMessage);
    };

  }, []);


  return (
    <div className="w-96">
      {connected ? <div>Connected</div> : <div>Not Connected</div>}
      <MainContainer>
        <ChatContainer>
          <MessageList>
            {messages.map((m,i) => m.type === "separator" ?
              <MessageSeparator key={i} {...m.props} /> :
              <Message key={i} model={{
                message: message.content,
                sentTime: "just now",
                sender: message.role,
              }} />)}
          </MessageList>
          <MessageInput placeholder="Type message here"/>
        </ChatContainer>
      </MainContainer>
    </div>
  )
}
