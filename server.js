const express = require("express");
const { Pool } = require("pg");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

const pool = new Pool({
  user: "usuario",
  host: "localhost",
  database: "supertrunfo",
  password: "senha",
  port: 5432
});

// rota que retorna os carros embaralhados
app.get("/api/deck", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM carros ORDER BY RANDOM()");
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(3001, () => {
  console.log("Servidor rodando em http://localhost:3001");
});
