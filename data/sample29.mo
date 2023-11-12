within AIFDJ.samples;
model sample1
  C C1(PR = 6.0, EFF = 0.85);
  C C2(PR = 3.06, EFF = 0.85);
  I I1(W = 75.0);
  H H1(T4 = 1800.0);
  H H2(T4 = 1200.0);
  T T1;
  S S1(B = 6.04);
  M M1;
  E E1;
  N N1;
equation
  connect(C1.portA, I1.portA);
  connect(H1.portA, C2.portB);
  connect(T1.portA, H1.portB);
  connect(C1.spool1, T1.spool2);
  connect(T1.spool1, C2.spool2);
  connect(S1.portA, C1.portB);
  connect(M1.portA, H2.portB);
  connect(M1.portB, E1.portC);
  connect(E1.portA, S1.portC);
  connect(E1.portB, M1.portC);
  connect(H2.portA, T1.portB);
  connect(C2.portA, S1.portB);
  connect(N1.portA, E1.portD);
end sample1;