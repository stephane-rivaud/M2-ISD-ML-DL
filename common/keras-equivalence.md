# PyTorch ↔ Keras equivalence

This module is in **PyTorch**. This page is a bridge for apprentices whose
company uses Keras / TensorFlow — **not** a second library to
install in session, **not** a stack change.

The identifiers below are those of the D1 lab (MLP, one logit output,
`BCE` "from logits", Adam). Keras 3 (`import keras`) and `tf.keras`
expose the same names.

## Table

| Step | PyTorch | Keras |
|---|---|---|
| Model definition | `nn.Sequential(...)` | `keras.Sequential([...])` |
| Loss | `nn.BCEWithLogitsLoss()` | `keras.losses.BinaryCrossentropy(from_logits=True)` |
| Optimiser | `torch.optim.Adam(model.parameters(), lr=1e-3)` | `keras.optimizers.Adam(learning_rate=1e-3)` |
| Training loop | `zero_grad` → forward → `backward` → `step` | `model.compile(...)` then `model.fit(...)` |
| Evaluation | `model.eval()` + `torch.no_grad()` | `model.evaluate(x, y)` |

Same ideas (tensor, loss, step, epoch). Keras **compiles** the loss and
the optimiser once, then `fit` hides the loop. PyTorch has you
write it — that is deliberate in this module.

Classification into $C$ classes: `nn.CrossEntropyLoss` on the PyTorch side,
`keras.losses.CategoricalCrossentropy(from_logits=True)` on the Keras side
(logits, no softmax in the model).

## The same five lines, in code

PyTorch (D1 sketch):

```python
model = nn.Sequential(nn.Linear(n_in, 32), nn.ReLU(), nn.Linear(32, 1))
criterion = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
# in the loop, for each batch (xb, yb):
optimizer.zero_grad()
loss = criterion(model(xb).squeeze(-1), yb)
loss.backward()
optimizer.step()
model.eval()
with torch.no_grad():
    logits = model(x_test)
```

Keras:

```python
model = keras.Sequential([
    keras.layers.Dense(32, activation="relu"),
    keras.layers.Dense(1),
])
model.compile(
    loss=keras.losses.BinaryCrossentropy(from_logits=True),
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
)
model.fit(x_train, y_train, epochs=40, validation_data=(x_val, y_val))
model.evaluate(x_test, y_test)
```

`model.fit` expects arrays (or a `tf.data` / `keras.utils.PyDataset`),
not a PyTorch `DataLoader`. D1's `pos_weight` translates as
`keras.losses.BinaryCrossentropy(..., from_logits=True)` plus
sample weighting (`class_weight` on `fit`), not as an identical
`pos_weight` tensor.

## What this sheet is not

Not a Keras course. Not an invitation to `pip install tensorflow` this Monday.
If the company uses Keras, reread the table; the empirical protocol
(Problem → … → Recommendation) does not change with the library.
