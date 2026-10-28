package com.salati.ads;
import java.util.*;
import java.util.concurrent.Executor;

public final class AdInitializationTest {
 static final class Queue implements Executor {
  final ArrayDeque<Runnable> tasks = new ArrayDeque<>();
  public void execute(Runnable task) { tasks.add(task); }
  void drain() { while (!tasks.isEmpty()) tasks.remove().run(); }
 }
 static final class Sdk {
  boolean initialized; int configured, ready, failed, started; Runnable callback;
  void initialize(Runnable done) { started++; callback = () -> { initialized = true; done.run(); }; }
  void configure() { if (!initialized) throw new IllegalStateException("initialize must precede mute/volume"); configured++; }
 }
 static void check(boolean ok) { if (!ok) throw new AssertionError(); }
 public static void main(String[] args) {
  Sdk sdk = new Sdk(); Queue worker = new Queue(), ui = new Queue(); AdInitialization gate = new AdInitialization();
  // Reproduce the same invalid order enforced by Google's SDK bytecode.
  try { sdk.configure(); throw new AssertionError("Pre-initialization config must fail"); } catch (IllegalStateException expected) {}
  Runnable start = () -> gate.start(worker, ui, sdk::initialize, sdk::configure, () -> sdk.ready++, e -> sdk.failed++);
  start.run(); start.run(); check(sdk.started == 0 && sdk.configured == 0);
  worker.drain(); check(sdk.started == 1 && sdk.configured == 0 && sdk.ready == 0);
  sdk.callback.run(); sdk.callback.run(); check(sdk.configured == 0);
  ui.drain(); check(sdk.configured == 1 && sdk.ready == 1 && sdk.failed == 0);
  start.run(); worker.drain(); check(sdk.started == 1);

  for (Throwable error : new Throwable[]{new IllegalStateException("SDK init"), new NoClassDefFoundError("SDK class")}) {
   int[] counts = new int[2]; AdInitialization failing = new AdInitialization();
   failing.start(Runnable::run, Runnable::run, done -> { if (error instanceof RuntimeException) throw (RuntimeException)error; throw (LinkageError)error; },
    () -> counts[0]++, () -> counts[0]++, e -> { check(e == error); counts[1]++; });
   check(counts[0] == 0 && counts[1] == 1);
  }
  int[] failed = {0}, ready = {0};
  new AdInitialization().start(Runnable::run, Runnable::run, Runnable::run,
   () -> { throw new IllegalStateException("Configuration failed"); }, () -> ready[0]++, e -> failed[0]++);
  check(failed[0] == 1 && ready[0] == 0);
  Queue lateUi = new Queue(); Sdk late = new Sdk(); AdInitialization canceled = new AdInitialization();
  canceled.start(Runnable::run, lateUi, late::initialize, late::configure, () -> late.ready++, e -> late.failed++);
  late.callback.run(); canceled.cancel(); lateUi.drain(); check(late.configured == 0 && late.ready == 0 && late.failed == 0);
  Queue canceledWorker = new Queue(); AdInitialization beforeStart = new AdInitialization(); Sdk never = new Sdk();
  beforeStart.start(canceledWorker, Runnable::run, never::initialize, never::configure, () -> never.ready++, e -> never.failed++);
  beforeStart.cancel(); canceledWorker.drain(); check(never.started == 0);
  int[] rejected = {0};
  new AdInitialization().start(task -> { throw new IllegalStateException("Worker rejected"); }, Runnable::run,
   Runnable::run, () -> {}, () -> {}, e -> rejected[0]++);
  check(rejected[0] == 1);
  System.out.println("PASS: SDK pre-init regression, deferred configuration, UI dispatch, duplicate init/callbacks, runtime/linkage failures, configuration failure, cancellation and worker rejection.");
 }
}
