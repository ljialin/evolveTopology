within AIFDJ.samples;
model sample1
  C C1(PR = 5.51, EFF = 0.85);
  I I1(W = 65.0);
  H H1(T4 = 1800.0);
  H H2(T4 = 1200.0);
  S S1(B = 3.07);
  T T1;
  N N1;
  O O1;
equation
  connect(C1.portA, I1.portA);
  connect(H1.portA, S1.portB);
  connect(T1.portA, H1.portB);
  connect(T1.spool1, C1.spool2);
  connect(H2.portA, T1.portB);
  connect(S1.portA, C1.portB);
  connect(N1.portA, S1.portC);
  connect(O1.portA, H2.portB);
end sample1;