clear all;
clc;
close all;

K = 4.647;         
Tp1 = 85.759;        
Tp2 = 3.5463;        
Td = 2.1816;        

T_eff = Tp1;  
L_delay = Tp2;
L_eff = Td + L_delay;

s = tf('s');

G_original = (K* exp(-L_delay*s) / ((1 + Tp1*s)*(1 + Tp2*s))) ;
G_app = (K* exp(-L_eff*s) / (T_eff*s + 1) );

figure;
step(G_app, 'k', G_original, 'g')
title('Step Response of Original and Approximated System');
legend('Approximated System' ,'Original System');
grid on;

text(150, 1.5, sprintf('$G_{app}(s) = \\frac{%g e^{-%gs}}{%gs + 1}$', K, L_eff, T_eff), ...
    'Interpreter', 'latex', 'FontSize', 25, 'Color', 'k');
hold off;

%ZN parameters
Kp=2.83;
Ki =0.168;
controller1 = tf([Kp Ki], [1 0]); 
tf1 = controller1 * G_app;
sys_cl = feedback(controller1 * G_app, 1);

% Second controller parameters
newKp = 1.5;
newKi = 0.03;
controller2 = tf([newKp newKi], [1 0]);
tf2 = controller2 * G_app;
sys_c2 = feedback(controller2 * G_app, 1);

t = 0:0.1:200;      

[y1, t] = step(sys_cl, t); 
[y2, t] = step(sys_c2, t); 

% step responses 
figure;
plot(t, y1, 'b-', 'LineWidth', 2); hold on; % ZN response
plot(t, y2, 'g-', 'LineWidth', 2);          % Second system response
title('Step Responses of Both Systems');
xlabel('Time (s)');
ylabel('Output ');
legend('tuned with NZ' ,'fine-tuned');
grid on;
hold off;

figure;
bode(tf1, 'b', tf2, 'g', {0.01, 10}); 
title('Bode Plot ');
legend('tuned with NZ' ,'fine-tuned');
grid on;
hold off;
