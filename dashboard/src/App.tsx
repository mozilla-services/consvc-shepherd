import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    try {
      const response = axios.get("http://127.0.0.1:8000/api/v1/test_models/");
      setItems(response.data);
      console.log(response.data);
    } catch (error) {
      console.error("There was an error fetching the test items!", error);
    }
  }, []);

  return (
    <>
      <div className="App">
        <header className="App-header">
          <h1>Welcome to My App</h1>
        </header>
        <div>
          <h1>Languages</h1>
          <ul>
            {items.map((item) => (
              <li
                key={item.name}
                style={{
                  listStyleType: "none",
                  padding: "10px",
                  fontSize: "20px",
                }}
              >
                {item.name}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
}

export default App;
