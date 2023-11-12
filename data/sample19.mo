within AIFDJ.samples;
model sample1
  C C1(PR = 6.0, EFF = 0.85);
  C C2(PR = 4.04, EFF = 0.85);
  I I1(W = 75.0);
  H H1(T4 = 1620.0);
  H H2(T4 = 1260.0);
  S S1(B = 2.08);
  T T1;
  T T2;
  M M1;
  N N1;
equation
  connect(C1.portA, I1.portA);
  connect(H1.portA, S1.portB);
  connect(T1.portA, M1.portC);
  connect(C1.spool1, T2.spool2);
  connect(T1.spool1, C2.spool2);
  connect(H2.portA, T1.portB);
  connect(S1.portA, C1.portB);
  connect(M1.portA, T2.portB);
  connect(M1.portB, C2.portB);
  connect(C2.portA, S1.portC);
  connect(T2.portA, H1.portB);
  connect(N1.portA, H2.portB);
end sample1;