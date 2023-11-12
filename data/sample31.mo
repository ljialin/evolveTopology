within AIFDJ.samples;
model sample1
  C C1(PR = 5.02, EFF = 0.85);
  C C2(PR = 3.55, EFF = 0.85);
  I I1(W = 75.0);
  H H1(T4 = 1740.0);
  H H2(T4 = 1200.0);
  S S1(B = 5.05);
  T T1;
  M M1;
  E E1;
  N N1;
equation
  connect(C1.portA, I1.portA);
  connect(H1.portA, S1.portB);
  connect(T1.portA, H1.portB);
  connect(T1.spool1, C1.spool2);
  connect(S1.portA, C1.portB);
  connect(M1.portA, H2.portB);
  connect(M1.portB, C2.portB);
  connect(E1.portA, S1.portC);
  connect(E1.portB, M1.portC);
  connect(H2.portA, T1.portB);
  connect(C2.portA, E1.portC);
  connect(C2.spool1, T1.spool2);
  connect(N1.portA, E1.portD);
end sample1;