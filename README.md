# vhs_snd

## Конфигурация.

- Частота дискретизации: $sr$ (например, 44100 Гц, как и показано в коде).
- Аудиоданные: $x(t)$, где $t = \frac{n}{sr}$, $n = 0,1,2,\dots,N-1$.

## Формулы эффекта.

### 1. VHS шум (hiss).

Добавляем белый гауссов шум с амплитудой $A_{\text{hiss}}$:

```math
h_{\text{hiss}}(t) \sim \mathcal{N}(0, A_{\text{hiss}}^2)
```

где шум дополнительно модулируется случайным коэффициентом $m(t) \in [0.5, 1.5]$:

```math
h_{\text{hiss}}^{\prime}(t) = h_{\text{hiss}}(t) \cdot m(t)
```

### 2. Гул сети (hum).

Добавляем синусоидальный гул с частотой $f_{\text{hum}} \) (обычно 50 или 60 Гц) и амплитудой \( A_{\text{hum}}$:

```math
h_{\text{hum}}(t) = A_{\text{hum}} \cdot \sin(2 \pi f_{\text{hum}} t)
```

### 3. Вибрация громкости (volume vibrato).

Случайная модуляция громкости:

```math
v_{\text{vib}}(t) = 1 + \delta v(t), \quad \delta v(t) \in [-0.025, 0.025]
```

### 4. Выпадения сигнала (dropouts).

В определённых случайных интервалах $I_i = [t_i, t_i + \Delta t_i]$ амплитуда сигнала понижается случайно на коэффициент $d_i \in [0.2, 0.6]$:

```math
d(t) = 
\begin{cases}
d_i, & t \in I_i \\
1, & \text{иначе}
\end{cases}
```

### 5. Щелчки (clicks).

Добавляются импульсы со спадающей амплитудой длительностью \( L \) с начальной амплитудой 1:

```math
c_i(t) = 
\begin{cases}
1 - \frac{t - t_i}{L}, & t_i \leq t < t_i + L \\
0, & \text{иначе}
\end{cases}
```

Общий сигнал щелчков:

```math
c(t) = \sum_i c_i(t)
```

### 6. Wow & Flutter (модуляция времени).

Медленная и быстрая модуляция времени с частотами $f_{\text{wow}}$ и $f_{\text{flutter}}$:

```math
\Delta t_{\text{wow}}(t) = A_{\text{wow}} \cdot \sin(2 \pi f_{\text{wow}} t), \quad
\Delta t_{\text{flutter}}(t) = A_{\text{flutter}} \cdot \sin(2 \pi f_{\text{flutter}} t)
```

Изменённое время:

```math
t' = t + \Delta t_{\text{wow}}(t) + \Delta t_{\text{flutter}}(t)
```

Обработка аудио по новому времени:

```math
x'(t) = x(t')
```

### 7. Эхо (echo).

Добавляется эхо с задержкой $\tau$ и коэффициентом затухания $\alpha$:

```math
e(t) = \alpha \cdot x'(t - \tau), \quad \tau > 0
```

### 8. Итоговый сигнал.

Итоговый сигнал с учётом всех эффектов:

```math
y(t) = \bigl( x'(t) + e(t) \bigr) \cdot v_{\text{vib}}(t) \cdot d(t) + h_{\text{hiss}}^{\prime}(t) + h_{\text{hum}}(t) + 0.1 \cdot c(t)
```

### 9. Сатурация (ограничение амплитуды).

Применяется мягкая сатурация с помощью гиперболического тангенса:

```math
y_{\text{sat}}(t) = \frac{\tanh(3 y(t))}{3}
```
