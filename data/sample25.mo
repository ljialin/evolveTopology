within AIFDJ.samples;
model sample1
  C C1(PR = 6.0, EFF = 0.85);
  C C2(PR = 4.53, EFF = 0.85);
  I I1(W = 75.0);
  H H1(T4 = 1740.0);
  H H2(T4 = 1680.0);
  S S1(B = 4.06);
  T T1;
  M M1;
  N N1;
equation
  connect(C1.portA, I1.portA);
  connect(H1.portA, S1.portB);
  connect(C1.spool1, T1.spool2);
  connect(H2.portA, M1.portC);
  connect(S1.portA, C1.portB);
  connect(M1.portA, T1.portB);
  connect(M1.portB, C2.portB);
  connect(C2.portA, S1.portC);
  connect(T1.portA, H1.portB);
  connect(T1.spool1, C2.spool2);
  connect(N1.portA, H2.portB);
end sample1;