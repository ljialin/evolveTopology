within AIFDJ.samples;
model sample1
  C C1(PR = 4.04, EFF = 0.85);
  C C2(PR = 6.0, EFF = 0.85);
  I I1(W = 75.0);
  H H1(T4 = 1200.0);
  S S1(B = 9.01);
  S S2(B = 1.09);
  T T1;
  M M1;
  E E1;
  O O1;
  N N1;
equation
  connect(C1.portA, I1.portA);
  connect(H1.portA, S2.portB);
  connect(T1.portA, M1.portC);
  connect(T1.spool1, C1.spool2);
  connect(S1.portA, E1.portD);
  connect(O1.portA, E1.portC);
  connect(S2.portA, C1.portB);
  connect(M1.portA, H1.portB);
  connect(M1.portB, C2.portB);
  connect(C2.portA, S2.portC);
  connect(C2.spool1, T1.spool2);
  connect(E1.portA, S1.portC);
  connect(E1.portB, T1.portB);
  connect(N1.portA, S1.portB);
end sample1;