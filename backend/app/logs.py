import csv
import os
from datetime import datetime
from typing import Optional, Dict, Iterable, Any
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# /d:/codigos/python/Projeto_IntegradorVI/backend/app/logs.py

class RLTrainingCSVLogger:
    """
    Logger que grava métricas de treinamento (accuracy, precision, recall, f1, loss, etc.) em CSV.
    Uso:
      logger = RLTrainingCSVLogger("logs/rl_training.csv")
      logger.log(epoch=1, step=100, accuracy=0.92, precision=0.90, recall=0.93, f1=0.915, loss=0.2)
      # ou passar dict de métricas
      logger.log_metrics_dict({"accuracy":0.92, "f1":0.915}, epoch=1)
    """

    DEFAULT_FIELDS = ["timestamp", "epoch", "step", "accuracy", "precision", "recall", "f1", "loss", "notes"]

    def __init__(self, filepath: str, fieldnames: Optional[Iterable[str]] = None, append: bool = True):
        self.filepath = filepath
        self.fieldnames = list(fieldnames) if fieldnames else list(self.DEFAULT_FIELDS)
        # allow additional custom fields later when logging dicts
        self._ensure_dir()
        if not append or not os.path.exists(self.filepath):
            # create file with header
            self._write_header()

    def _ensure_dir(self):
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _write_header(self):
        with open(self.filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()

    def _maybe_extend_header(self, new_keys: Iterable[str]):
        new_keys = [k for k in new_keys if k not in self.fieldnames]
        if not new_keys:
            return
        # read existing rows, rewrite with extended header
        rows = []
        if os.path.exists(self.filepath):
            with open(self.filepath, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    rows.append(r)
        self.fieldnames.extend(new_keys)
        with open(self.filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

    def _row_base(self, epoch: Optional[int], step: Optional[int], notes: Optional[str]) -> Dict[str, Any]:
        return {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "epoch": epoch if epoch is not None else "",
            "step": step if step is not None else "",
            "notes": notes or ""
        }

    def log(self,
            epoch: Optional[int] = None,
            step: Optional[int] = None,
            accuracy: Optional[float] = None,
            precision: Optional[float] = None,
            recall: Optional[float] = None,
            f1: Optional[float] = None,
            loss: Optional[float] = None,
            notes: Optional[str] = None,
            extras: Optional[Dict[str, Any]] = None):
        """
        Grava uma linha no CSV com os campos fornecidos.
        Campos não fornecidos ficam vazios.
        extras: dicionário de métricas adicionais (serão adicionadas como colunas se necessário).
        """
        row = self._row_base(epoch, step, notes)
        if accuracy is not None:
            row["accuracy"] = float(accuracy)
        if precision is not None:
            row["precision"] = float(precision)
        if recall is not None:
            row["recall"] = float(recall)
        if f1 is not None:
            row["f1"] = float(f1)
        if loss is not None:
            row["loss"] = float(loss)
        if extras:
            # convert extras values to simple types (str/float/int)
            for k, v in extras.items():
                row[str(k)] = v

        # ensure header contains any extra keys
        extra_keys = [k for k in (extras.keys() if extras else []) if k not in self.fieldnames]
        if extra_keys:
            self._maybe_extend_header(extra_keys)

        # write row
        with open(self.filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            # fill missing keys with empty string
            out = {k: row.get(k, "") for k in self.fieldnames}
            writer.writerow(out)

    def log_metrics_dict(self, metrics: Dict[str, Any], epoch: Optional[int] = None, step: Optional[int] = None, notes: Optional[str] = None):
        """
        Grava métricas a partir de um dicionário (ex: {'accuracy':..., 'f1':..., 'recall':...}).
        """
        # separate known fields
        known = {k: metrics.get(k) for k in ("accuracy", "precision", "recall", "f1", "loss")}
        extras = {k: v for k, v in metrics.items() if k not in known or known[k] is None and k in metrics}
        # merge known if present
        self.log(epoch=epoch, step=step, accuracy=known.get("accuracy"),
                 precision=known.get("precision"), recall=known.get("recall"),
                 f1=known.get("f1"), loss=known.get("loss"),
                 notes=notes, extras=extras or None)

    def log_from_sklearn(self, y_true, y_pred, epoch: Optional[int] = None, step: Optional[int] = None, average: str = "binary", notes: Optional[str] = None):
        """
        Se sklearn estiver instalado, calcula accuracy, precision, recall, f1 e grava.
        """
        try:
        except Exception as e:
            raise RuntimeError("sklearn não instalado ou não disponível") from e

        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, average=average))
        rec = float(recall_score(y_true, y_pred, average=average))
        f1 = float(f1_score(y_true, y_pred, average=average))
        self.log(epoch=epoch, step=step, accuracy=acc, precision=prec, recall=rec, f1=f1, notes=notes)

# exemplo rápido de uso (remova ou comente em produção)
if __name__ == "__main__":
    logger = RLTrainingCSVLogger("../logs/rl_training.csv")
    logger.log(epoch=1, step=100, accuracy=0.92, precision=0.90, recall=0.93, f1=0.915, loss=0.23, notes="primeiro teste")
    logger.log_metrics_dict({"accuracy": 0.93, "f1": 0.92, "val_loss": 0.2}, epoch=1, step=200)