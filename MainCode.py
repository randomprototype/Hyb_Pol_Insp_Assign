"""
Victor Hugo Resende Lima
vhugoreslim@gmail.com

Esse código necessita dos seguintes pacotes nas respectivas versões:
Pillow==9.0.1
scipy==1.7.3
streamlit==1.5.0
click==8
"""
import streamlit as st
import numpy as np
import sys
from streamlit import cli as stcli
from scipy.integrate import quad #Single integral
from PIL import Image

def main():
    #criando 3 colunas
    col1, col2, col3= st.columns(3)
    foto = Image.open('randomen.png')
    #st.sidebar.image("randomen.png", use_column_width=True)
    #inserindo na coluna 2
    col2.image(foto, use_column_width=True)
    #O código abaixo insere o título, mas não centraliza.
    #st.title('KMT Policy Software')
    #O código abaixo centraliza e atribui cor
    st.markdown("<h2 style='text-align: center; color: #306754;'>Hybrid Inspection and Age-Based Policy with Inspector Assignment</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background-color: #F3F3F3; padding: 10px; text-align: center;">
          <p style="font-size: 20px; font-weight: bold;">A Delay-Time Model for Non-Periodic Inspection Intervals and Inspector Team Assignment</p>
          <p style="font-size: 15px;">By: Victor H. R. Lima, Cristiano A. V. Cavalcante & Phuc Do</p>
        </div>
        """, unsafe_allow_html=True)

    menu = ["Cost-rate", "Information", "Website"]
    
    choice = st.sidebar.selectbox("Select here", menu)
    
    if choice == menu[0]:
        st.header(menu[0])
        st.subheader("Insert the parameter values below:")
        
        Eta1=st.number_input("Insert the characteristic life of the weak component ($\\eta_{1}$)", min_value = 0.0, value = 3.0)
        Beta1=st.number_input("Insert the shape parameter of the weak component ($\\beta_{1}$)", min_value = 0.0, value = 3.0)
        Eta2=st.number_input("Insert the characteristic life of the strong component ($\\eta_{2}$)", min_value = 3.0, value = 12.0)
        Beta2=st.number_input("Insert the shape parameter of the strong component ($\\beta_{2}$)", min_value = 0.0, value = 3.0) 
        p=st.number_input("Insert the mixture parameter ($p$)", min_value = 0.0, value = 0.15)
        Lambda=st.number_input("Insert the rate of the exponential distribution for delay-time ($\\lambda$)", min_value = 0.0, value = 2.0)
        FixedCosts=st.text_input("Insert the fixed costs of the inspectors ($C^H$)")
        Ci=st.text_input("Insert the inspection costs of the inspectors ($C^I$)")
        Alpha=st.text_input("Insert the false-positive values of the inspectors ($\\alpha$)")
        Beta=st.text_input("Insert the false-negative values of the inspectors ($\\beta$)")
        Cr=st.number_input("Insert cost of replacement (inspections and age-based) ($C^R$)", min_value = 0.5, value = 1.5)
        Cf=st.number_input("Insert cost of failure ($C^F$)", min_value = 5, value = 15)

        FixedCosts=FixedCosts.split()
        Ci=Ci.split()
        Alpha=Alpha.split()
        Beta=Beta.split()
        for _ in range(0,len(FixedCosts),1):
            FixedCosts[_]=float(FixedCosts[_])
            Ci[_]=float(Ci[_])
            Alpha[_]=float(Alpha[_])
            Beta[_]=float(Beta[_])
        
        st.subheader("Insert the variable values below:")
        Delta=st.text_input("Insert the inspection moments ($\\Delta$)")
        Y=st.text_input("Insert the sequence of inspectors ($Y$)")
        T=st.number_input("Insert the age-based preventive action ($T$)")
        
        Delta=Delta.split()
        Y=Y.split()
        for _ in range(0,len(Delta),1):
            Delta[_]=float(Delta[_])
            Y[_]=float(Y[_])
        K=len(Delta)
        Delta.insert(0,0)
        Y.insert(0,-1)

        def KD_KT(K,delta,Y,T):
            ############Defect arrival component 1#####################################
            def f01(x):
                return (Beta1/Eta1)*((x/Eta1)**(Beta1-1))*np.exp(-(x/Eta1)**Beta1)
            ############Defect arrival component 2#####################################
            def f02(x):#
                return (Beta2/Eta2)*((x/Eta2)**(Beta2-1))*np.exp(-(x/Eta2)**Beta2)
            ###########Mixture for defect arrival######################################
            def fx(x):
                return (p*f01(x))+((1-p)*f02(x))
            ##########Delay-time distribution##########################################
            def fh(h):
                return Lambda*np.exp(-Lambda*h)
            ##########Cumulative for defect arrival####################################
            def Fx(x):
                return (p*(1-np.exp(-(x/Eta1)**Beta1)))+((1-p)*(1-np.exp(-(x/Eta2)**Beta2)))
            #########Reliability function for defect arrival###########################
            def Rx(x):
                return 1-Fx(x)
            ##########Cumulative function delay-time###################################
            def Fh(h):
                return 1-np.exp(-Lambda*h)
            ##########Reliability function delay-time##################################
            def Rh(h):
                return np.exp(-Lambda*h)

            #####OBS: THE SOLUTION CONTAINS DELTA[0]=0, Y[0]=-1

            ############Scenario 1: Defect arrival and failure between inspections#####
            def C1():
                PROB1=0
                EC1=0
                EL1=0
                for i in range(0, K):
                    InspectionCost=0
                    TotalAlpha=1
                    for j in range(0,i+1,1):
                        if (j!=0):
                            InspectionCost+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    PROB1+=TotalAlpha*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], (delta[i+1]),0,lambda x:(delta[i+1])-x)[0])
                    EL1+=TotalAlpha*(dblquad(lambda h, x: (x+h)*fx(x)*fh(h), delta[i], (delta[i+1]),0,lambda x:(delta[i+1])-x)[0])
                    EC1+=(InspectionCost+Cf)*(TotalAlpha*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], (delta[i+1]),0,lambda x:(delta[i+1])-x)[0]))
                return PROB1, EC1, EL1
            
            ############Scenario 2: Defect arrival and surviving until next inspection without error at inspection####
            def C2():
                PROB2=0
                EC2=0
                EL2=0
                for i in range(0, K):
                    InspectionCost=0
                    TotalAlpha=1
                    for j in range(0,i+1,1):
                        if (j!=0):
                            InspectionCost+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    #####Counting the last inspection where there is no false positive#########
                    InspectionCost+=Ci[Y[i+1]]
                    ###################################################################
                    PROB2+=TotalAlpha*(1-Beta[Y[i+1]])*(quad(lambda x: fx(x)*(1-Fh((delta[i+1])-x)),delta[i], (delta[i+1]))[0])
                    EC2+=(InspectionCost+Cr)*(TotalAlpha*(1-Beta[Y[i+1]])*(quad(lambda x: fx(x)*(1-Fh((delta[i+1])-x)),delta[i], (delta[i+1]))[0]))
                    EL2+=(delta[i+1])*(TotalAlpha*(1-Beta[Y[i+1]])*(quad(lambda x: fx(x)*(1-Fh((delta[i+1])-x)),delta[i], (delta[i+1]))[0]))
                return PROB2, EC2, EL2
            
            ##########Scenario 3: Defect arrival after inspections and failure#########
            def C3():
                InspectionCost=0
                TotalAlpha=1
                for j in range(0,K+1,1):
                    if (j!=0):
                        InspectionCost+=Ci[Y[j]]
                        TotalAlpha*=(1-Alpha[Y[j]])
                PROB3=TotalAlpha*(dblquad(lambda h, x: fx(x)*fh(h), delta[K], T,0,lambda x:T-x)[0])
                EC3=(InspectionCost+Cf)*PROB3
                EL3=TotalAlpha*(dblquad(lambda h, x: (x+h)*fx(x)*fh(h), delta[K], T,0,lambda x:T-x)[0])
                return PROB3, EC3, EL3
            
            ###########Scenario 4: Defect arrival after inspections and preventive at T####
            def C4():
                InspectionCost=0
                TotalAlpha=1
                for j in range(0,K+1,1):
                    if (j!=0):
                        InspectionCost+=Ci[Y[j]]
                        TotalAlpha*=(1-Alpha[Y[j]])
                PROB4=TotalAlpha*quad(lambda x: fx(x)*(1-Fh(T-x)),delta[K],T)[0]
                EC4=(InspectionCost+Cr)*PROB4
                EL4=T*PROB4
                return PROB4, EC4, EL4
            
            ##########Scenario 5: No defect arrival####################################
            def C5():
                InspectionCost=0
                TotalAlpha=1
                for j in range(0,K+1,1):
                    if (j!=0):
                        InspectionCost+=Ci[Y[j]]
                        TotalAlpha*=(1-Alpha[Y[j]])
                PROB5=TotalAlpha*Rx(T)
                EC5=(InspectionCost+Cr)*PROB5
                EL5=T*PROB5
                return PROB5, EC5, EL5
            
            ##########Scenario 6: Defect arrival and sucessive false negatives at inspections#####
            def C6():
                PROB6=0
                EC6=0
                EL6=0
                for i in range(0, K-1):
                    #####Computing the total alpha#############
                    InspectionCost1=0
                    TotalAlpha=1
                    for j in range(0,i+1,1):
                        if (j!=0):
                            InspectionCost1+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    ###########################################
                    for j in range(i+1, K):
                        #####Computing the total beta##########
                        InspectionCost=InspectionCost1
                        TotalBeta=1
                        for k in range(i+1,j+1,1):
                            InspectionCost+=Ci[Y[k]]
                            TotalBeta*=Beta[Y[k]]
                        ###############################################################
                        PROB6+=TotalAlpha*TotalBeta*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], (delta[i+1]),lambda x:(delta[j])-x,lambda x:(delta[j+1])-x)[0])
                        EL6+=TotalAlpha*TotalBeta*(dblquad(lambda h, x: (x+h)*fx(x)*fh(h), delta[i], (delta[i+1]),lambda x:(delta[j])-x,lambda x:(delta[j+1])-x)[0])
                        EC6+=(InspectionCost+Cf)*(TotalAlpha*TotalBeta*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], (delta[i+1]),lambda x:(delta[j])-x,lambda x:(delta[j+1])-x)[0]))
                return PROB6, EC6, EL6
            
            ##########Scenario 7: Defect arrival inside inspection phase with false negatives and a true positive####
            def C7():
                PROB7=0
                EC7=0
                EL7=0
                for i in range(0, K-1):
                    #######Computing the total alpha##############################
                    InspectionCost1=0
                    TotalAlpha=1
                    for j in range(0,i+1,1):
                        if (j!=0):
                            InspectionCost1+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    ##############################################################
                    for j in range(i+2,K+1,1):
                        InspectionCost=InspectionCost1
                        TotalBeta=1
                        for k in range(i+1,j):
                            InspectionCost+=Ci[Y[k]]
                            TotalBeta*=Beta[Y[k]]
                        ######Counting the last inspection#############################
                        InspectionCost+=Ci[Y[j]]
                        ###############################################################
                        PROB7+=TotalAlpha*TotalBeta*(1-Beta[Y[j]])*(quad(lambda x: fx(x)*Rh((delta[j])-x),delta[i], (delta[i+1]))[0])
                        EC7+=(InspectionCost+Cr)*(TotalAlpha*TotalBeta*(1-Beta[Y[j]])*(quad(lambda x: fx(x)*Rh((delta[j])-x),delta[i], (delta[i+1]))[0]))
                        EL7+=(delta[j])*(TotalAlpha*TotalBeta*(1-Beta[Y[j]])*(quad(lambda x: fx(x)*Rh((delta[j])-x),delta[i], (delta[i+1]))[0]))
                return PROB7, EC7, EL7
            
            ##########Scenario 8: False positive at inspection########################
            def C8():
                PROB8=0
                EC8=0
                EL8=0
                for i in range(0,K):
                    TotalAlpha=1
                    InspectionCost=0
                    for j in range(0,i+1,1):
                        if (j!=0):
                            InspectionCost+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    InspectionCost+=Ci[Y[i+1]]
                    PROB8+=TotalAlpha*Alpha[Y[i+1]]*Rx(delta[i+1])
                    EC8+=(InspectionCost+Cr)*TotalAlpha*Alpha[Y[i+1]]*Rx(delta[i+1])
                    EL8+=(delta[i+1]*(TotalAlpha*Alpha[Y[i+1]]*Rx(delta[i+1])))
                return PROB8, EC8, EL8
            
            ##########Scenario 9: Sucessive false negatives and failure after inspections#####
            def C9():
                PROB9=0
                EC9=0
                EL9=0
                for i in range(0,K):
                    ######Counting inspections before i############################
                    InspectionCost=0
                    TotalAlpha=1
                    for j in range(0,i+1):
                        if (j!=0):
                            InspectionCost+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    ########COunting inspections after i until K-th####################
                    TotalBeta=1
                    for j in range(i+1,K+1,1):
                        InspectionCost+=Ci[Y[j]]
                        TotalBeta*=Beta[Y[j]]
                    PROB9+=(TotalAlpha*TotalBeta*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], delta[i+1],lambda x: delta[K]-x, lambda x:T-x)[0]))
                    EC9+=(InspectionCost+Cf)*((TotalAlpha*TotalBeta*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], delta[i+1],lambda x:delta[K]-x, lambda x:T-x)[0])))
                    EL9+=((TotalAlpha*TotalBeta*(dblquad(lambda h, x: (x+h)*fx(x)*fh(h), delta[i], delta[i+1],lambda x:delta[K]-x, lambda x:T-x)[0])))
                return PROB9, EC9, EL9
            
            #########Scenario 10: Sucessive false negatives and renovation at T########
            def C10():
                PROB10=0
                EC10=0
                EL10=0
                for i in range(0,K):
                    #######Counting inspections before i###############################
                    InspectionCost=0
                    TotalAlpha=1
                    for j in range(0,i+1):
                        if (j!=0):
                            InspectionCost+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    #######Counting inspections after i until K-th#####################
                    TotalBeta=1
                    for j in range(i+1,K+1,1):
                        InspectionCost+=Ci[Y[j]]
                        TotalBeta*=Beta[Y[j]]
                    PROB10+=TotalAlpha*TotalBeta*(quad(lambda x: fx(x)*Rh(T-x),delta[i], (delta[i+1]))[0])
                    EC10+=(InspectionCost+Cr)*(TotalAlpha*TotalBeta*(quad(lambda x: fx(x)*Rh(T-x),delta[i], (delta[i+1]))[0]))
                    EL10+=T*(TotalAlpha*TotalBeta*(quad(lambda x: fx(x)*Rh(T-x),delta[i], (delta[i+1]))[0]))
                return PROB10, EC10, EL10
            
            ########Defining variables based on previous functions#####################
            C1=C1()
            C2=C2()
            C3=C3()
            C4=C4()
            C5=C5()
            C6=C6()
            C7=C7()
            C8=C8()
            C9=C9()
            C10=C10()
            
            ########Defining cost and life based on previous scenarios#################
            # TOTAL_PB=C1[0]+C2[0]+C3[0]+C4[0]+C5[0]+C6[0]+C7[0]+C8[0]+C9[0]+C10[0]
            TOTAL_EC=C1[1]+C2[1]+C3[1]+C4[1]+C5[1]+C6[1]+C7[1]+C8[1]+C9[1]+C10[1]
            TOTAL_EL=C1[2]+C2[2]+C3[2]+C4[2]+C5[2]+C6[2]+C7[2]+C8[2]+C9[2]+C10[2]
            ########Increasing cost with the fixed cost of the inspector###############
            Used=[]
            for i in range(0,len(FixedCosts),1):
                Used.append(0)
            for i in range(1,len(Y),1):
                Used[Y[i]]+=1
            for i in range(0,len(FixedCosts),1):
                if (Used[i]>0):
                    TOTAL_EC+=FixedCosts[i]
            return TOTAL_EC/TOTAL_EL
        
        st.subheader("Click on botton below to run this application:")    
        botao = st.button("Get cost-rate")
        if botao:
            CR=KD_KT(K, Delta, Y, T)
            CRs=[]
            for i in range(0,len(Y),1):
                Assing=[]
                for j in range(1,len(Y),1):
                    Assing.append(i)
                CRs.append(KD_KT(K, Delta, Assing, T))
            
            ####################### EXECUTA OTIMIZADOR#$#################################
            st.write("---RESULT---")
            st.write("Cost-rate", CR)
            
    if choice == menu[1]:
        st.header(menu[1])
        st.write("<h6 style='text-align: justify; color: Blue Jay;'>This prototype was created by members of the RANDOM research group, which aims to assist in the application of the {W, M} policy developed in the paper 'On periodic maintenance for a protection system'.</h6>", unsafe_allow_html=True)
        st.write("<h6 style='text-align: justify; color: Blue Jay;'>This prototype has restrictions regarding the solution search space. If it is in the user's interest to use a wider range of solution combinations or if there is any question about the study and/or this prototype can be directed to any of the email addresses below. Also, this application is still in the development stage. Finally, if this application is used for any purpose, all authors should be informed.</h6>", unsafe_allow_html=True)
        
        st.write('''

v.h.r.lima@random.org.br

c.a.v.cavalcante@random.org.br

''' .format(chr(948), chr(948), chr(948), chr(948), chr(948)))       
    if choice==menu[2]:
        st.header(menu[2])
        
        st.write('''The Research Group on Risk and Decision Analysis in Operations and Maintenance was created in 2012 
                 in order to bring together different researchers who work in the following areas: risk, maintenance a
                 nd operation modelling. Learn more about it through our website.''')
        st.markdown('[Click here to be redirected to our website](http://random.org.br/en/)',False)        
if st._is_running_with_streamlit:
    main()
else:
    sys.argv = ["streamlit", "run", sys.argv[0]]
    sys.exit(stcli.main())
