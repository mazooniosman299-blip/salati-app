package com.salati.ads;

import java.util.concurrent.Executor;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;

/** Orders SDK initialization and configuration across worker/UI callbacks. */
public final class AdInitialization {
 public interface Starter { void start(Runnable complete); }
 private final AtomicBoolean started = new AtomicBoolean();
 private final AtomicBoolean terminal = new AtomicBoolean();
 public void cancel() { terminal.set(true); }
 public void start(Executor worker, Executor ui, Starter starter, Runnable configure,
                   Runnable ready, Consumer<Throwable> failure) {
  if (!started.compareAndSet(false, true) || terminal.get()) return;
  try {
   worker.execute(() -> {
    if (terminal.get()) return;
    try {
     starter.start(() -> deliver(ui, () -> {
      if (!terminal.compareAndSet(false, true)) return;
      try { configure.run(); ready.run(); }
      catch (RuntimeException | LinkageError error) { failure.accept(error); }
     }, failure));
    } catch (RuntimeException | LinkageError error) { reject(ui, error, failure); }
   });
  } catch (RuntimeException | LinkageError error) { reject(ui, error, failure); }
 }
 private void reject(Executor ui, Throwable error, Consumer<Throwable> failure) {
  deliver(ui, () -> { if (terminal.compareAndSet(false, true)) failure.accept(error); }, failure);
 }
 private void deliver(Executor ui, Runnable task, Consumer<Throwable> failure) {
  try { ui.execute(task); }
  catch (RuntimeException | LinkageError error) {
   if (terminal.compareAndSet(false, true)) failure.accept(error);
  }
 }
}
