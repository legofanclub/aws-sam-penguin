// @ts-nocheck
import { useState, useRef, useMemo } from "react";
import React from "react";
import Sketch from "react-p5";
import "./App.css";

import backgroundPic from "./assets/Action_Dance_Light_Blue.webp";
import penguinPic from "./assets/Default_Location.webp";

function canvasHeight() {
  return Math.trunc(window.innerWidth * (3 / 4) * (9 / 16));
}
function canvasWidth() {
  return Math.trunc(window.innerWidth * (3 / 4));
}

function App() {
  const [name, setName] = useState("example name");
  const [chat, setChat] = useState("example message");
  const [joinButtonMessage, setJoinButtonMessage] = useState("connecting to server");
  const [connected, setConnected] = useState(false);
  const websocketRef = useRef();

  const propsRef = useRef({ chat: chat, name: name });

  const Sketch = useMemo(() => {
    websocketRef.current = new WebSocket(
      "wss://fut2pn5a74.execute-api.us-west-2.amazonaws.com/Prod"
    );
    websocketRef.current.addEventListener("open", () => {
      console.log("connected!!");
      setConnected(true);
      setJoinButtonMessage("join server")
    })
    return (
      <SK all={Object.assign(propsRef.current, { ws: websocketRef.current })} />
    );
  }, []);

  function sendChatMessage() {
    const message = `{"type": "chat", "data": "${chat}"}`;
    websocketRef.current.send(message);
    setChat("");
  }

  function joinServer() {
    const message = JSON.stringify({
      type: "join_server",
      data: { name: name, color: "none" },
    });
    websocketRef.current.send(message);

    (function askForID() {
      const message = '{"type": "get_id"}';
      websocketRef.current.send(message);
    })();

    (function askForInitialDB() {
      const message = '{"type": "get_table_data"}';
      websocketRef.current.send(message);
    })();
  }

  const handleEnterPressedOnChat = (event) => {
    if (event.key === "Enter") {
      sendChatMessage();
    }
  };

  return (
    (connected ? <div>
      <div style={{ position: "relative" }}>
        {Sketch}
        <input
          type="text"
          onKeyDown={handleEnterPressedOnChat}
          value={chat}
          onChange={(e) => setChat(e.target.value)}
          style={{
            position: "absolute",
            left: `${canvasWidth() * (1 / 10)}px`,
            top: `${(canvasHeight() * 9) / 10}px`,
            width: `${canvasWidth() * (6 / 10)}px`,
          }}
        />
        <button
          onClick={() => {
            sendChatMessage();
          }}
          style={{
            position: "absolute",
            left: `${canvasWidth() * (7.5 / 10)}px`,
            top: `${(canvasHeight() * 9) / 10 - 10}px`,
          }}
        >
          send chat message
        </button>
      </div>
      <div style={{ display: "flex", flexDirection: "row" }}>
        <div
          style={{
            outlineWidth: "1px",
            outlineColor: "black",
            outlineStyle: "solid",
            marginRight: "10px",
            padding: "10px",
          }}
        >
          <InputBox
            name="type name and press join to join server"
            val={name}
            onChange={(e) => {
              setName(e.target.value);
            }}
          />
          <button
            onClick={() => {
              joinServer();
            }}
          >
            {joinButtonMessage}
          </button>
        </div>
      </div>
    </div> : <p> loading </p>)
  );
}

const SK = (props) => {
  const ws = props.all.ws;
  let yourID = "";
  const penguins = {};
  let penguinImage;
  let backgroundImage;

  let _p5;

  const preload = (p5) => {
    _p5 = p5;
    // dancing gif
    penguinImage = p5.loadImage(backgroundPic);
    backgroundImage = p5.loadImage(penguinPic);
    penguinImage.pause();
  };

  const setup = (p5, canvasParentRef) => {
    p5.textAlign(p5.CENTER);
    p5.imageMode(p5.CENTER);

    const canvasInstance = p5
      .createCanvas(canvasWidth(), canvasHeight())
      .parent(canvasParentRef);

    const mouseClickedCallback = () => {
      // hack to pass p5 parameter to _mouseClicked
      _mouseClicked(p5);
    };
    canvasInstance.mouseClicked(mouseClickedCallback);

    ws.addEventListener("message", (e) => {
      handleMessage(e.data, p5);
    });
  };

  function handleMessage(message) {
    try {
      JSON.parse(message);
    } catch {
      return null;
    }
    message = JSON.parse(message);
    if (message.type == "move") {
      if (message.data.id != yourID) {
        penguins[message.data.id].idealX = (message.data.x * _p5.width) / 100;
        penguins[message.data.id].idealY = (message.data.y * _p5.height) / 100;
      }
    }
    if (message.type == "chat") {
      penguins[message.data.id].chat = message.data.text;
      setTimeout(() => {
        penguins[message.data.id].chat = "";
      }, 5000);
    }
    if (message.type == "id") {
      yourID = message.data;
    }
    if (message.type == "leaving") {
      delete penguins[message.data];
    }
    if (message.type == "new_penguin") {
      for (const p of message.data) {
        if (p.PK != yourID) {
          penguins[p.PK] = new Penguin(
            (p.position_x * _p5.width) / 100,
            (p.position_y * _p5.height) / 100,
            p.name,
            p.color,
            p.PK
          );
        } else {
          // hack to fix a bug that is possibly related to db not being updated in time to get correct name
          penguins[p.PK].name = p.name;
        }
      }
    }
    if (message.type == "set_db") {
      for (const p of message.data) {
        penguins[p.PK] = new Penguin(
          (p.position_x * _p5.width) / 100,
          (p.position_y * _p5.height) / 100,
          p.name,
          p.color,
          p.PK
        );
      }
    }
  }

  function movePenguin() {
    const message = JSON.stringify({
      type: "move",
      data: {
        position_x: Math.trunc((_p5.mouseX / _p5.width) * 100),
        position_y: Math.trunc((_p5.mouseY / _p5.height) * 100),
      },
    });
    ws.send(message);
  }

  function draw(p5) {
    p5.background(220);
    drawBackground(p5);
    for (const key of Object.keys(penguins)) {
      penguins[key].updateAndDraw(p5);
    }
  }

  class Penguin {
    constructor(x, y, name, color, id) {
      this.x = x;
      this.y = y;
      this.name = name;
      this.color = color;
      this.id = id;
      this.chat = "";
      this.idealX = x;
      this.idealY = y;
      this.PENGUIN_SPEED = 2;
    }

    setDestination(x, y) {
      this.idealX = x;
      this.idealY = y;
    }

    updateAndDraw() {
      this.move(_p5);
      this.draw(_p5);
    }

    move() {
      const xDistance = Math.abs(this.idealX - this.x);
      const yDistance = Math.abs(this.idealY - this.y);
      const hypotenuse = Math.sqrt(xDistance ** 2 + yDistance ** 2);

      if (hypotenuse > 1) {
        this.x = _p5.lerp(this.x, this.idealX, this.PENGUIN_SPEED / hypotenuse);
        this.y = _p5.lerp(this.y, this.idealY, this.PENGUIN_SPEED / hypotenuse);
      }
    }

    draw() {
      _p5.translate(this.x, this.y);
      this.drawPenguinBody(_p5);
      this.drawNametag(_p5);
      this.drawChat(_p5);
      _p5.translate(-this.x, -this.y);
    }

    drawPenguinBody() {
      _p5.image(
        penguinImage,
        0,
        0,
        100,
        100,
        0,
        0,
        penguinImage.width,
        penguinImage.height,
        _p5.CONTAIN,
        _p5.LEFT
      );
    }

    drawNametag() {
      _p5.textAlign(_p5.CENTER);
      _p5.text(this.name, 0, 33);
    }

    drawChat() {
      _p5.textAlign(_p5.CENTER);
      _p5.text(this.chat, 0, -50);
    }
  }

  function drawBackground() {
    _p5.imageMode(_p5.CORNER);
    _p5.background(backgroundImage);
    _p5.imageMode(_p5.CENTER);
  }

  function _mouseClicked() {
    penguins[yourID].setDestination(_p5.mouseX, _p5.mouseY);
    movePenguin(_p5);
  }

  return <Sketch setup={setup} draw={draw} preload={preload} />;
};

function InputBox(props) {
  return (
    <div>
      <h3>{props.name}</h3>
      <input
        value={props.val}
        style={{ marginBottom: "20px" }}
        onChange={(e) => {
          props.onChange(e);
        }}
      ></input>
    </div>
  );
}

export default App;
